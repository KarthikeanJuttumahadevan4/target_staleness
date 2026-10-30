# 02_RAG_Requirements_Analysis.md – Independent RAG Requirements Analysis

## 1. Introduction

This document expands on the approved **01_RAG_Proposal.md** by specifying detailed functional and non-functional requirements for the Independent RAG System. It defines the ingestion pipeline, data schemas, comparison logic, and inconsistency resolution workflow required to build a RAG system that operates completely independently of the Knowledge Graph (KG) and can later be compared against it.

### 1.1 References
- **01_RAG_Proposal.md** – Approved proposal outlining the core goal and high-level workflow.
- **extract.py** – Existing timestamp extraction utility to be reused for `as_of` timestamps.

### 1.2 Terminology
| Term | Definition |
|------|-----------|
| **RAG Deduction** | A structured fact extracted or inferred by the independent RAG system. |
| **KG Fact** | A fact stored in the existing Temporal Knowledge Graph. |
| **Chunk** | A contiguous segment of a source document used for embedding. |
| **Vector Index** | A standalone search index (e.g., Qdrant) storing embeddings and metadata. |
| **Provenance** | Metadata tracking the source file, extraction path, and timestamp for a deduction. |
| **Temporal Validity** | The `as_of` timestamp determining which version of a fact is current. |

---

## 2. Functional Requirements

### 2.1 Ingestion

#### **FR-ING-001: File Ingestion**
The system **shall** ingest files from the `samples5/` directory **without** accessing any KG services (Neo4j, KG schema, or KG APIs).

- **Supported File Types**: `.txt`, `.pdf`, `.docx`, `.xlsx`, `.pptx`
- **Input Sources**: File system path (`samples5/`)
- **Trigger Modes**: 
  - Batch mode ( voll ingestion of existing files)
  - Watch mode (incremental updates via file system watcher)

#### **FR-ING-002: File Validation**
The system **shall** validate each file before processing:
- Check file exists and is readable
- Verify file size > 0 bytes
- Detect file type mismatches (e.g., `.pdf` extension but not a PDF)
- **On Failure**: Skip the file and log an error with file path and reason.

#### **FR-ING-003: Timestamp Extraction**
The system **shall** use `extract.py` to obtain the **modification/edit timestamp** for each file:
- Primary: Extract timestamp from file metadata or embedded markers
- Fallback: Use `os.path.getmtime` if `extract.py` fails
- **Output**: `as_of` (ISO 8601 datetime string) + `timestamp_fallback` (boolean)

#### **FR-ING-004: Incremental Detection**
The system **shall** support incremental ingestion:
- Track previously ingested files by `file_path` + `file_hash` (SHA-256)
- Skip files with unchanged hashes
- Re-process files with new hashes or new `as_of` timestamps

---

### 2.2 Chunking

#### **FR-CHK-001: Chunking Strategy**
The system **shall** split source documents into semantic chunks to balance context and granularity:
- **Text Files**: Split by paragraphs or sentences (min 50 tokens, max 512 tokens)
- **PDFs**: Split by pages or logical sections
- **Excel**: Split by sheets, then by rows (treat each row as a record)
- **Word**: Split by paragraphs or headings
- **PowerPoint**: Split by slides, then by bullet points

#### **FR-CHK-002: Overlap for Context**
The system **shall** include overlap between chunks to preserve context:
- **Default Overlap**: 20% of chunk size (configurable)
- **Minimum Overlap**: 1 sentence or 10 tokens

#### **FR-CHK-003: Metadata Preservation**
Each chunk **shall** carry metadata for traceability:
```json
{
  "chunk_id": "<file_path>_<hash>_<index>",
  "file_path": "samples5/invoices/INV-2024-001.pdf",
  "file_hash": "sha256:abc123",
  "as_of": "2024-09-01T00:00:00+00:00",
  "chunk_index": 0,
  "total_chunks": 5,
  "start_offset": 0,
  "end_offset": 512
}
```

#### **FR-CHK-004: Table Handling**
The system **shall** preserve table structure:
- Excel: Treat each row as a separate chunk with column headers as metadata
- PDF Tables: Extract as markdown tables or structured objects
- **Output**: Include `table_headers` and `row_number` in metadata

---

### 2.3 Embedding

#### **FR-EMB-001: Embedding Model**
The system **shall** use a **local** embedding model (no external API calls):
- **Model Options**: `sentence-transformers/all-MiniLM-L6-v2` (preferred, if available locally)
- **Fallback**: `BAAI/bge-small-en-v1.5` (if installed in local environment)
- **Dimensions**: 384 (all-MiniLM-L6-v2) or 512 (bge-small)
- **Normalization**: L2-normalize embeddings before indexing

#### **FR-EMB-002: Embedding Generation**
The system **shall** generate embeddings for:
- Each chunk (primary)
- Each deducted fact (optional, for fact-level retrieval)
- **Batch Processing**: Embed multiple chunks in a single batch for efficiency

#### **FR-EMB-003: Embedding Storage**
The system **shall** store embeddings in a **standalone vector index** (independent of Neo4j):
- **Vector Store**: Qdrant (already available in environment)
- **Collection Name**: `rag_deductions`
- **Payload Schema**: Includes all chunk metadata + deducted facts

---

### 2.4 Retrieval

#### **FR-RET-001: Query Processing**
The system **shall** accept free-form text queries:
- **Input**: User query (string)
- **Preprocessing**: Lowercase, remove stopwords, extract keywords
- **Embedding**: Generate query embedding using same model as ingestion

#### **FR-RET-002: Vector Search**
The system **shall** perform similarity search:
- **Algorithm**: Cosine similarity (default) or dot product
- **Top-K**: Return top 10 chunks by default (configurable)
- **Filters**: Support filtering by `file_path`, `as_of` range, or metadata

#### **FR-RET-003: Result Ranking**
The system **shall** rank results by:
1. Similarity score (primary)
2. Temporal recency (`as_of` timestamp, secondary)
3. Confidence score (if available from fact deduction)

#### **FR-RET-004: Deduction Generation**
The system **shall** generate structured deductions from retrieved chunks:
- **Method**: Use regex patterns, keyword extraction, or lightweight LLM (if available)
- **Fallback**: Return raw text if structured deduction fails
- **Minimum Confidence**: 0.7 (configurable threshold)

---

### 2.5 Fact Deduction

#### **FR-DED-001: Deduction Schema**
All deductions **shall** conform to the following schema (designed for comparison with KG facts):
```json
{
  "deduction_id": "<unique_id>",
  "source_file_path": "samples5/invoices/INV-2024-001.pdf",
  "chunk_id": "INV-2024-001_abc123_0",
  "as_of": "2024-09-01T00:00:00+00:00",
  "subject_entity": "Product_X",
  "predicate": "has_price",
  "object_value": "100",
  "object_type": "numeric",
  "extraction_method": "regex",
  "confidence": 0.95,
  "provenance": {
    "extraction_path": "text",
    "model_used": "sentence-transformers/all-MiniLM-L6-v2",
    "raw_text": "Product X price is 100"
  }
}
```

#### **FR-DED-002: Entity Normalization**
The system **shall** normalize entities for comparison:
- **Text Normalization**: Lowercase, strip whitespace, remove punctuation
- **Numeric Extraction**: Extract numbers from text (e.g., "$100" → `100`)
- **Entity Resolution**: Map raw text to canonical entities (e.g., "Prod X" → "Product_X")

#### **FR-DED-003: Predicate Mapping**
The system **shall** map natural language to standard predicates:
| Natural Language | Predicate | Example |
|-----------------|-----------|---------|
| `price is`, `cost` | `has_price` | "Product X price is 100" |
| `date`, `as of` | `has_date` | "Report date 2024-10-01" |
| `headcount`, `employees` | `has_headcount` | "Headcount: 150" |
| `budget`, `allocated` | `has_budget` | "Budget Q3: $450000" |

#### **FR-DED-004: Deduction Storage**
The system **shall** store deductions in two places:
1. **Vector Index Payload** (for retrieval efficiency)
2. **JSON Lines File** (for persistence and comparison): `RAG_data/deductions.jsonl`

---

## 3. Data Schema for Comparison

### 3.1 RAG Deduction Schema (Full)

```json
{
  "deduction_id": "string (UUID)",
  "source_file_path": "string",
  "chunk_id": "string",
  "as_of": "ISO 8601 datetime string",
  "subject_entity": "string",
  "subject_entity_type": "string (optional, e.g., 'product', 'report')",
  "predicate": "string",
  "object_value": "string | number | boolean",
  "object_type": "string (enum: 'text', 'numeric', 'boolean', 'date')",
  "extraction_method": "string (enum: 'regex', 'keyword', 'table', 'llm')",
  "confidence": "float (0.0-1.0)",
  "provenance": {
    "extraction_path": "string (enum: 'text', 'pdf_text', 'ocr', 'excel_table', 'docx_text', 'pptx_text')",
    "model_used": "string",
    "raw_text": "string"
  },
  "metadata": {
    "file_hash": "string",
    "chunk_index": "int",
    "total_chunks": "int",
    "page_number": "int (optional)",
    "table_headers": "list (optional)",
    "row_number": "int (optional)"
  }
}
```

### 3.2 KG Fact Schema (for reference)

From existing Temporal KG system:
```json
{
  "fact_id": "string",
  "entity_id": "string",
  "predicate": "string",
  "object_value": "string",
  "as_of": "ISO 8601 datetime string",
  "current": "boolean",
  "superseded_by": "string (optional)",
  "supersedes": "list (optional)",
  "valid_from": "ISO 8601 datetime string (optional)",
  "valid_to": "ISO 8601 datetime string (optional)",
  "provenance_id": "string"
}
```

### 3.3 Alignment Mapping

| RAG Field | KG Field | Notes |
|-----------|----------|-------|
| `deduction_id` | `fact_id` | Both are unique identifiers |
| `source_file_path` | (from Provenance) | RAG uses direct path, KG uses provenance node |
| `as_of` | `as_of` | Direct match |
| `subject_entity` | `entity_id` | May require normalization |
| `predicate` | `predicate` | Direct match |
| `object_value` | `object_value` | May require type coercion |
| `object_type` | (N/A) | RAG-specific metadata |
| `confidence` | (N/A) | RAG-specific metadata |

---

## 4. Comparison and Alignment Logic

### 4.1 Alignment Strategy

#### **FR-CMP-001: Key-Based Alignment**
The system **shall** align RAG deductions with KG facts using composite keys:
1. **Exact Match**: `subject_entity` + `predicate` + `source_file_path`
2. **Fuzzy Match**: `subject_entity` + `predicate` (ignoring source)
3. **Semantic Match**: Use embeddings to find similar facts (similarity > 0.85)

#### **FR-CMP-002: Value Normalization for Comparison**
Before comparison, the system **shall** normalize values:
- **Numeric**: Extract first number from string (e.g., "$100" → `100`, "Price: 100 USD" → `100`)
- **Currency**: Strip currency symbols and normalize to base unit
- **Dates**: Parse all date formats to ISO 8601
- **Text**: Lowercase, remove punctuation, strip whitespace

#### **FR-CMP-003: Confidence Thresholds**
Alignment **shall** require minimum confidence scores:
- **Exact Match**: Confidence = 1.0 (always align)
- **Fuzzy Match**: Confidence ≥ 0.9
- **Semantic Match**: Confidence ≥ 0.85

#### **FR-CMP-004: Multi-Match Handling**
If multiple KG facts match a single RAG deduction:
1. Prefer facts with matching `source_file_path`
2. If still multiple, prefer `current=true` facts
3. If still multiple, prefer most recent `as_of`

---

### 4.2 Inconsistency Detection

#### **FR-CMP-005: Inconsistency Types**
The system **shall** classify inconsistencies into types:

| Type | Condition | Severity | Example |
|------|-----------|----------|---------|
| **Exact Match** | Values match after normalization | INFO | Both: `price=100` |
| **Value Conflict** | Same key, different values | HIGH | RAG: `100`, KG: `120` |
| **RAG Missing** | RAG has no deduction for a KG fact | MEDIUM | KG: `price=100`, RAG: ∅ |
| **KG Missing** | KG has no fact for a RAG deduction | MEDIUM | RAG: `price=100`, KG: ∅ |
| **Temporal Conflict** | Same value, different `as_of` | MEDIUM | RAG: `as_of=2024-10-01`, KG: `as_of=2024-09-01` |
| **Type Mismatch** | Same key, different `object_type` | LOW | RAG: numeric `100`, KG: text `"100 USD"` |
| **Interpretation Conflict** | Same source text, different deduced facts | MEDIUM | RAG: `price=100`, KG: `cost=100` |

#### **FR-CMP-006: Grouping by Entity**
The system **shall** group inconsistencies by `subject_entity` + `predicate` for efficient reporting.

---

## 5. Inconsistency Resolution

### 5.1 Automatic Resolution Rules (Expanded)

The following rules **shall** be applied in priority order.

| Rule ID | Condition | Resolution Action | Priority | Notes |
|---------|-----------|-------------------|----------|-------|
| **R1** | Values match after normalization (`value_r == value_k`) | **No action** (mark as `CONSISTENT`) | N/A | Always apply first |
| **R2** | Same `source_file_path`, same `predicate`, **RAG `as_of` > KG `as_of`** | **Prefer RAG**: Mark KG fact as superseded, adopt RAG value | **P0** | Temporal validity |
| **R3** | Same `source_file_path`, same `predicate`, **KG `as_of` > RAG `as_of`** | **Prefer KG**: Discard RAG deduction, keep KG fact | **P0** | Temporal validity |
| **R4** | Same `source_file_path`, same `predicate`, **RAG has explicit table data** (extraction_path=excel_table) | **Prefer RAG**: Table data > text inference | **P1** | Structured > unstructured |
| **R5** | Same `source_file_path`, same `predicate`, **KG has explicit provenance chain** (`supersedes` exists) | **Prefer KG**: KG has stronger audit trail | **P1** | Audit reliability |
| **R6** | Numeric conflict, **RAG value is extracted from table**, KG from text | **Prefer RAG**: Table extraction > regex | **P2** | Precision preference |
| **R7** | Date conflict, **RAG date parsed from ISO format**, KG from natural text | **Prefer RAG**: Structured date > inferred date | **P2** | Precision preference |
| **R8** | All else | **Escalate to Human** | **P3** | Requires manual review |

### 5.2 Resolution Workflow

```
For each inconsistency:
    1. Apply rules R1-R8 in priority order
    2. If a rule matches:
          - Apply resolution action
          - Log: {inconsistency_id, rule_applied, action_taken, timestamp}
          - Mark as RESOLVED
    3. If no rule matches:
          - Generate Human Escalation Report
          - Mark as ESCALATED
          - PAUSE processing (require human decision)
```

### 5.3 Human Escalation Report (Expanded Format)

The system **shall** generate reports in the following format:

```markdown
# Inconsistency Report #<UUID>

## 📋 Summary
- **Status**: ⏳ Awaiting Human Decision
- **Reported At**: <ISO 8601 timestamp>
- **Severity**: HIGH | MEDIUM | LOW

## 🔍 Conflict Details
- **Conflict Type**: <Value Conflict | Missing Fact | Temporal Conflict | ...>
- **Entity**: `<subject_entity>`
- **Predicate**: `<predicate>`

## 📊 RAG Deduction
- **ID**: `<deduction_id>`
- **Value**: `<object_value>`
- **Type**: `<object_type>`
- **Extraction Method**: `<extraction_method>`
- **Confidence**: `<confidence>`
- **Source File**: `<source_file_path>`
- **As Of**: `<as_of>`
- **Extraction Path**: `<extraction_path>`
- **Raw Text**: ```<raw_text>```

## 💾 KG Fact
- **ID**: `<fact_id>`
- **Value**: `<object_value>`
- **Current**: `<current>`
- **As Of**: `<as_of>`
- **Valid From**: `<valid_from>`
- **Valid To**: `<valid_to>`
- **Supersedes**: `<supersedes>`
- **Source**: (from provenance)

## ⚖️ Resolution Attempt
- **Rules Applied**: [R1, R2, R3]
- **Blocking Rule**: <rule_id>
- **Reason**: <human-readable explanation>

## 🤔 Recommended Action
- **Option 1**: Prefer RAG value
  - **Pros**: <reasoning>
  - **Cons**: <downsides>
- **Option 2**: Prefer KG value
  - **Pros**: <reasoning>
  - **Cons**: <downsides>
- **Option 3**: Manual correction
  - **Pros**: Highest accuracy
  - **Cons**: Time-consuming

## 📝 Human Decision
[ ] Approve Option 1
[ ] Approve Option 2
[ ] Approve Option 3
[ ] Reject (provide feedback below)

**Comments**: ________________________________
**Decision By**: _____________________________
**Decision At**: _____________________________
```

### 5.4 Resolution Logging

All resolutions **shall** be logged to `RAG_data/resolution_log.jsonl` with schema:
```json
{
  "report_id": "UUID",
  "inconsistency_id": "UUID",
  "rule_applied": "R2",
  "action": "PREFER_RAG",
  "timestamp": "ISO 8601",
  "resolved_by": "auto | human",
  "notes": "string"
}
```

---

## 6. Non-Functional Requirements

### 6.1 Performance

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| **Ingestion Throughput** | ≥ 100 files/minute | Files ingested / time |
| **Indexing Latency** | ≤ 500ms per file | Time to embed + index |
| **Query Latency** | ≤ 200ms (P95) | Time from query to first result |
| **Memory Usage** | ≤ 4GB for 10,000 files | Max RSS during ingestion |
| **Vector Index Size** | ≤ 500MB for 10,000 chunks | On-disk size |

### 6.2 Independence from Neo4j

The system **shall NOT**:
- Import any KG-specific modules (e.g., `temporal.temporal_kg`)
- Connect to Neo4j (`bolt://`) at any point
- Use KG schema definitions or constraints
- Depend on KG being available or running

**Verification**: All imports **shall** be scanned to ensure no KG dependencies exist.

### 6.3 Testability

#### **NFR-TEST-001: Unit Tests**
- All core functions **shall** have unit tests
- Minimum test coverage: **80%**
- Tests **shall** use mock data (no real KG required)

#### **NFR-TEST-002: Integration Tests**
- Tests **shall** verify end-to-end workflow:
  - Ingest `samples5/` → Generate deductions → Store in vector index
  - Query → Retrieve deductions → Compare against planted KG facts
  - Detect planted inconsistencies → Apply auto-resolution
- Tests **shall** start/stop a local Qdrant instance for isolation

#### **NFR-TEST-003: Inconsistency Detection Tests**
- **Test Dataset**: Create a controlled dataset with known inconsistencies
- **Expected Detection Rate**: ≥ 90% of planted inconsistencies
- **Expected Auto-Resolution Rate**: ≥ 80% of detected inconsistencies

#### **NFR-TEST-004: Regression Tests**
- Deductions **shall** remain stable for unchanged input files
- Re-running ingestion on same files **shall** produce identical deductions

### 6.4 Reliability

| Requirement | Target |
|-------------|--------|
| **Error Handling** | No crashes on malformed files |
| **Retry Logic** | Automatic retry for transient failures (max 3 attempts) |
| **Data Integrity** | SHA-256 verification of all stored deductions |
| **backup** | Daily JSONL dump of all deductions |

### 6.5 Maintainability

- **Code Style**: Follow PEP 8 guidelines
- **Documentation**: All public functions **shall** have docstrings
- **Configuration**: All parameters (chunk size, overlap, etc.) **shall** be configurable via environment variables
- **Modularity**: Each component (ingestion, chunking, embedding, retrieval) **shall** be in its own module

---

## 7. Open Questions

| ID | Question | Impact | Proposed Answer | Status |
|----|---------|--------|-----------------|--------|
| **OQ-001** | Which embedding model is available in the local environment? | High | Use `sentence-transformers/all-MiniLM-L6-v2` if installed, else `BAAI/bge-small-en-v1.5` | Requires verification |
| **OQ-002** | Should the vector index be ephemeral (in-memory) or persistent (on-disk)? | Medium | On-disk for durability and testing | **Open** |
| **OQ-003** | What confidence threshold should be used for fact deduction? | Medium | Start with 0.7, tune based on test data | **Open** |
| **OQ-004** | Should we support incremental updates or only batch ingestion? | Medium | Support both via file watcher | **Open** |
| **OQ-005** | How to handle files that fail to embed (e.g., corrupt PDFs)? | Low | Log error, skip file, continue processing | **Open** |
| **OQ-006** | What chunk size and overlap provide optimal retrieval quality? | Medium | 512 tokens, 20% overlap (configurable) | **Open** |
| **OQ-007** | Should we include the raw chunk text in the deduction schema? | Low | Yes, for debugging and human review | **Open** |

---

## 8. Risks and Mitigations

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| **RK-001** | Embedding model not available locally | Medium | High | Document exact model requirements; use fallback model |
| **RK-002** | Vector index grows too large for memory | Medium | Medium | Use Qdrant's on-disk storage; implement pagination |
| **RK-003** | Low precision/recall in fact deduction | High | High | Use rule-based extraction first, add LLM if needed; tune thresholds |
| **RK-004** | Inconsistency detection misses semantic conflicts | Medium | High | Implement fuzzy matching with configurable similarity thresholds |
| **RK-005** | Performance bottlenecks in ingestion | Medium | Medium | Batch processing; parallel chunking/embedding |
| **RK-006** | KG schema changes break comparison logic | Low | High | Freeze KG schema version for comparison; use flexible mapping |
| **RK-007** | Human escalation reports are too verbose | Low | Medium | Implement templates; allow customization |

---

## 9. Next Stage

**Awaiting human validation** of this requirements analysis before proceeding to **Stage 3 – Specifications** (`03_RAG_Specifications.md`).

---
**Status**: Draft awaiting explicit human approval
