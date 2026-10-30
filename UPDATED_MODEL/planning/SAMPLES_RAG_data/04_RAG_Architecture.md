---
format: html
---

# 04_RAG_Architecture.md – Independent RAG Architecture & Design

## 1. Overview

This document presents the **concrete architecture and design decisions** for the Independent RAG System, as specified in `03_RAG_Specifications.md`. It defines the technology stack, data flow, component interactions, and how complete independence from the Knowledge Graph is achieved.

### 1.1 References
- **01_RAG_Proposal.md** – Core goal and high-level workflow
- **02_RAG_Requirements_Analysis.md** – Detailed functional/non-functional requirements
- **03_RAG_Specifications.md** – Technical specifications, interfaces, and algorithms

### 1.2 Document Structure
1. **High-Level Component Diagram** – Visual (textual) representation of the architecture
2. **Technology Choices & Justifications** – Specific libraries and their rationale
3. **Data Flow** – End-to-end path from ingestion to comparison
4. **Independence From Knowledge Graph** – Architectural guarantees
5. **Deployment & Runtime** – Execution environment and constraints
6. **Design Trade-offs** – Key decisions and their implications

---

## 2. High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INDEPENDENT RAG SYSTEM                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐      │
│  │   samples5/     │────▶│ File Ingestor   │────▶│   Chunkers      │      │
│  │   (Source)      │     │ (ingestor.py)   │     │ (text_chunkers, │      │
│  └─────────────────┘     └─────────────────┘     │  table_chunkers) │      │
│                                                    └────────┬────────┘      │
│                                                             │                │
│                    ┌────────────────────────────────────────┼────────────┐  │
│                    ▼                                        ▼            │  │
│  ┌────────────────────────┐      ┌─────────────────────────────┐         │  │
│  │  Embedder              │      │ Fact Deducer                 │         │  │
│  │ (embedder.py)           │      │ (fact_deducer.py)            │         │  │
│  │ - all-MiniLM-L6-v2      │      │ - Regex patterns             │         │  │
│  │ - BAAI/bge-small (fall) │      │ - Table extraction            │         │  │
│  └────────────────────────┘      └─────────────┬───────────────┘         │  │
│                                                    │                     │  │
│                                                    ▼                     │  │
│                                             ┌──────────────────┐       │  │
│                                             │   Deductions     │       │  │
│                                             │ (RAGDeduction)   │       │  │
│                                             └────────┬─────────┘       │  │
│                                                      │                 │  │
│                          ┌───────────────────────────────┼────────────┐  │  │
│                          ▼                               ▼            │  │  │
│  ┌─────────────────────────┐       ┌───────────────────────┐          │  │
│  │  Vector Store           │       │  JSONL Store          │          │  │
│  │ (Qdrant:6333)            │       │ (deductions.jsonl)    │          │  │
│  │ - Collection:           │       │                       │          │  │
│  │   rag_deductions        │       │                       │          │  │
│  │ - Payload:              │       │                       │          │  │
│  │   Chunks + Deductions   │       │                       │          │  │
│  └─────────────────────────┘       └───────────────────────┘          │  │
│                                                                          │  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMPARISON MODULE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐      │
│  │ RAG Deductions  │────▶│    Aligner      │────▶│   Detector      │      │
│  │ (From JSONL)    │     │ (aligner.py)    │     │ (detectors.py)  │      │
│  └─────────────────┘     └────────┬────────┘     └────────┬────────┘      │
│                                            │                     │              │
│                                            ▼                     ▼              │
│                                   ┌──────────────────────────────┐          │
│                                   │   Inconsistencies            │          │
│                                   └──────────────┬───────────────┘          │
│                                                  │                         │
│                                  ┌───────────────▼───────────────┐        │
│                                  ▼                               ▼        │
│                         ┌───────────────┐             ┌───────────────┐  │
│                         │   Resolver    │             │   Reporter    │  │
│                         │ (resolver.py) │             │ (reports.py)  │  │
│                         └───────────────┘             └───────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUTS                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  - deductions.jsonl (RAG facts)                                            │
│  - resolution_log.jsonl (resolution history)                                │
│  - inconsistency_reports/ (human escalation reports)                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key**: `────▶` = Data flow, `│` = Separator, Boxes = Components

---

## 3. Technology Choices & Justifications

### 3.1 Vector Store: Qdrant

**Decision**: Use **Qdrant** (version 1.8.0+)

**Justification**:
| Criteria | Qdrant | Alternatives | Winner |
|----------|--------|--------------|--------|
| **Availability** | Already running in environment (`localhost:6333`) | FAISS, Weaviate | Qdrant |
| **Independence** | Standalone, no KG dependency | Neo4j Vector | Qdrant |
| **Performance** | Optimized for cosine similarity | All similar | Qdrant |
| **Payload Storage** | Rich payload support for metadata | FAISS limited | Qdrant |
| **Persistence** | On-disk storage, crash-safe | FAISS in-memory | Qdrant |
| **Scalability** | Handles 10K+ vectors efficiently | All similar | Qdrant |

**Configuration**:
- Collection: `rag_deductions`
- Vector size: 384 (all-MiniLM-L6-v2) or 512 (bge-small)
- Distance: Cosine
- Optimizers: Single segment for simplicity
- WAL: Enabled for durability

**Usage**:
- Primary index: Chunk embeddings for retrieval
- Secondary indices: `file_path`, `as_of`, `subject_entity` for filtering

---

### 3.2 Embedding Model: sentence-transformers/all-MiniLM-L6-v2

**Decision**: Use **sentence-transformers/all-MiniLM-L6-v2** as primary, **BAAI/bge-small-en-v1.5** as fallback

**Justification**:
| Model | Size | Dimensions | Speed | Accuracy | Local? |
|-------|------|------------|-------|----------|--------|
| all-MiniLM-L6-v2 | 80MB | 384 | Fast | High | ✅ Checked |
| bge-small-en | 100MB | 512 | Fast | High | ⚠️ Verify |
| all-mpnet-base-v2 | 420MB | 768 | Medium | Higher | ❌ Too large |

**Why all-MiniLM-L6-v2**:
- **Small footprint** (80MB) – suitable for development environment
- **Good performance** on STS benchmark (85.9%)
- **Fast inference** – critical for batch ingestion
- **Widely used** – well-tested, stable
- **Lazy loading** – only loads when needed, reducing startup time

**Fallback Logic**:
```python
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    try:
        model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    except ImportError:
        raise ImportError("No embedding model available. Install sentence-transformers or bge.")
```

---

### 3.3 File Parsers: Specialized Libraries

| File Type | Library | Justification |
|-----------|---------|---------------|
| **PDF** | `pdfplumber` | Accurate text extraction with layout preservation; handles tables |
| **PDF (Scanned/OCR)** | `pdf2image` + `pytesseract` | OCR for image-based PDFs; fallback when pdfplumber fails |
| **Word (DOCX)** | `python-docx` | Native support for DOCX format; preserves formatting |
| **Excel (XLSX/XLS)** | `openpyxl` | Full Excel support; handles formulas (as values) |
| **PowerPoint (PPTX)** | `python-pptx` | Extracts text from slides and shapes |
| **Text (TXT)** | Built-in `pathlib` | Simple file read |

**Extraction Strategy**:
1. Try primary parser based on file extension
2. If fails (e.g., corrupt PDF), try fallback
3. If all fail, log error and skip file
4. Always preserve raw text for provenance

---

### 3.4 Timestamp Extraction: extract.py

**Decision**: Reuse existing `extract.py` from parent project

**Justification**:
- Already proven and tested in production
- Provides `as_of` timestamps from file metadata and embedded markers
- Includes fallback to `os.path.getmtime`
- Maintains consistency with KG system timestamps

**Integration**:
```python
from src.temporal.timestamp_extractor import TimestampExtractor

extractor = TimestampExtractor()
as_of, fallback = extractor.get_as_of(file_path)
```

**Note**: This is the **only** dependency on the parent project's code. It is **not** a KG dependency – `timestamp_extractor.py` only uses filesystem operations and metadata parsing, no Neo4j or KG schema.

---

### 3.5 Programming Language & Framework

**Decision**: Pure Python 3.10+

**Justification**:
- **Environment constraint**: Must use existing environment (no new tool installs via network)
- **Compatibility**: All selected libraries support Python 3.10+
- **No Framework Overhead**: Avoids dependency on FastAPI/Flask for simplicity
- **Script-based**: Allows easy integration with existing fish/bash scripts

**Structure**:
- Modular Python packages (PEP 420 namespace packages)
- Type hints (PEP 484) for interface clarity
- No external web framework (CLI-first design)

---

## 4. Data Flow Architecture

### 4.1 End-to-End Data Flow

```
┌─────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  File   │────▶│ Ingestor ▶  │────▶│   Chunker    │────▶│   Embedder   │
│ (samples│     │ (Validation │     │ (Text/Table) │     │ (Vectorize)  │
│ 5/)     │     │  + Timestamp)│     │              │     │              │
└─────────┘     └─────────────┘     └──────────────┘     └──────────────┘
         │                       │                      │
         │                       ▼                      ▼
         │              ┌──────────────────────────────────────┐
         │              │           Chunk Store                │
         │              │  (In-memory cache during pipeline)   │
         │              └──────────────┬──────────────┬───────┘
         │                             │              │
         │                             ▼              ▼
         │              ┌──────────────────┐ ┌──────────────────┐
         │              │ Vector Store     │ │  Deduction       │
         │              │ (Qdrant:6333)    │ │  (fact_deducer)  │
         │              │ - embeddings     │ │ - structured     │
         │              │ - metadata       │ │   facts          │
         │              └──────────────────┘ └──────────┬───────┘
         │                                                  │
         │                                                  ▼
         │                           ┌──────────────────────────────┐
         │                           │   Deductions Storage         │
         │                           │ - deductions.jsonl           │
         │                           │ - Qdrant payloads            │
         │                           └──────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    INDEPENDENT OPERATION COMPLETE                        │
│           (No KG accessed. Vector index + JSONL file ready.)            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                              (Later...)
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMPARISON PHASE                                       │
│           (Reads RAG deductions + KG facts from separate sources)       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────┐     ┌─────────────┐     ┌────────────────────────────┐  │
│  │ RAG        │     │ KG Facts    │     │        Aligner             │  │
│  │ Deductions │────▶│ (from       │────▶│ (Match by entity+predicate) │  │
│  │ (JSONL)    │     │  Neo4j*     │     │                           │  │
│  └─────────────┘     └─────────────┘     └───────────┬──────────────┘  │
│                                                      │                  │
│                      ┌───────────────────────────────────▼───────┐     │
│                      │             Inconsistencies                 │     │
│                      └───────────────────┬───────────────┬─────────┘     │
│                                          │               │               │
│                                          ▼               ▼               │
│                                 ┌─────────────┐ ┌─────────────┐          │
│                                 │  Resolver   │ │  Reporter   │          │
│                                 │ (Auto-      │ │ (Human      │          │
│                                 │  resolve)   │ │  reports)   │          │
│                                 └─────────────┘ └─────────────┘          │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

*NOTE: KG Facts are read from Neo4j ONLY in the Comparison Module.
      The Independent RAG pipeline itself NEVER accesses Neo4j.
```

### 4.2 Phase 1: Independent RAG Ingestion Pipeline

**Input**: `samples5/` directory
**Output**:
- Qdrant collection: `rag_deductions` (embeddings + payloads)
- File: `RAG_data/deductions.jsonl` (all deductions)

**Steps**:
1. **File Ingestor** walks `samples5/` directory
2. For each file:
   a. Calculate SHA-256 hash
   b. Extract timestamp via `extract.py` → `as_of`
   c. If hash unchanged and `as_of` unchanged → skip
   d. Else → extract raw text using type-specific parser
3. **Chunker** splits raw text into semantic chunks
4. **Embedder** generates embeddings for each chunk
5. **Fact Deducer** extracts structured facts from chunks
6. Store:
   - Chunk + embedding → Qdrant
   - Deduction → Qdrant payload + `deductions.jsonl`

### 4.3 Phase 2: Comparison Module

**Input**:
- RAG deductions from `deductions.jsonl` or Qdrant
- KG facts from Neo4j query

**Output**:
- Inconsistency reports (if any)
- Resolution log (`resolution_log.jsonl`)

**Steps**:
1. Load RAG deductions from JSONL
2. Query KG for facts (via Neo4j driver)
3. **Aligner** matches deductions to facts
4. **Detector** identifies inconsistencies
5. **Resolver** applies automatic rules or escalates
6. Log all resolutions

### 4.4 Critical Data Transformations

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| Ingestion | File | Parse + Timestamp | Raw text + metadata |
| Chunking | Raw text | Split + Overlap | Chunks |
| Embedding | Chunks | Vectorize | Embeddings |
| Deduction | Chunks | Regex/Table extraction | RAGDeduction |
| Storage | Embeddings + Deductions | Index in Qdrant | Searchable vector store |
| Alignment | RAGDeduction + KGFact | Match + Normalize | Alignment |
| Detection | Alignment | Compare values/timestamps | Inconsistency |
| Resolution | Inconsistency | Apply rules | ResolutionResult |

---

## 5. Independence from Knowledge Graph

This section details **architectural guarantees** that the Independent RAG System **never** accesses or depends on the Knowledge Graph.

### 5.1 Physical Separation

| Component | KG Access? | Rationale |
|-----------|------------|-----------|
| File Ingestor | ❌ No | Only accesses filesystem (`samples5/`) |
| Chunkers | ❌ No | Pure text manipulation, no external calls |
| Embedder | ❌ No | Local model inference, no network |
| Vector Store (Qdrant) | ❌ No | Separate service on port 6333, not 7687 |
| Fact Deducer | ❌ No | Regex/table parsing, no KG schema |
| JSONL Storage | ❌ No | Local file, independent format |
| **Comparison Module** | ✅ **Yes** (INTENTIONAL) | Only reads KG facts for comparison (via Neo4j driver) |

### 5.2 Dependency Isolation

**Allowed Dependencies**:
```
RAG_data/
├── src/
│   ├── timestamp_extractor.py  # From parent project (filesystem only)
│   └── extract.py              # FROM parent project (filesystem only)
│
└── All other code: ZERO dependencies on src/temporal/ or src/ingestion/
```

**Dependency Check**:
```bash
# Verify no KG imports
grep -r "from temporal" RAG_data/src/ && echo "ERROR: KG dependency detected!"
grep -r "from ingestion" RAG_data/src/ && echo "ERROR: KG dependency detected!"
grep -r "from indexing" RAG_data/src/ && echo "ERROR: KG dependency detected!"
grep -r "neo4j" RAG_data/src/ --include="*.py" && echo "ERROR: Neo4j dependency detected!"
```

### 5.3 Runtime Independence

- **Qdrant**: Runs on separate port (6333) from Neo4j (7687)
- **No Shared State**: RAG deductions stored separately from KG facts
- **Independent Lifecycle**: RAG pipeline can run while KG is down
- **Read-Only KG Access**: Comparison module only **reads** from KG, never writes

### 5.4 Data Format Independence

| Field | RAG Format | KG Format | Conversion |
|-------|------------|-----------|------------|
| Entity | `subject_entity` (string) | `entity_id` (string) | Direct mapping |
| Predicate | `predicate` (string) | `predicate` (string) | Direct mapping |
| Value | `object_value` (string) | `object_value` (string) | Normalization required |
| Timestamp | `as_of` (ISO string) | `as_of` (ISO string) | Direct mapping |
| Provenance | Inline in deduction | Separate node | Flattened for RAG |

**Key Difference**: RAG stores provenance inline; KG uses separate nodes. The Comparison Module handles this mapping.

---

## 6. Deployment & Runtime Considerations

### 6.1 Execution Modes

| Mode | Use Case | Trigger | Persistence |
|------|----------|---------|-------------|
| **Batch Ingestion** | Initial load or full refresh | CLI command | Full overwrite |
| **Incremental Ingestion** | New/modified files | File watcher | Append only |
| **Query Mode** | Retrieval without ingestion | CLI/API | Read-only |
| **Comparison Mode** | Detect inconsistencies | CLI command | Read KG + RAG |

### 6.2 Runtime Dependencies

| Dependency | Source | Required | Fallback |
|------------|--------|----------|----------|
| Python | System | ✅ Yes | N/A |
| Qdrant | Local service | ✅ Yes | In-memory (dev only) |
| pdfplumber | pip package | ⚠️ If PDFs exist | Skip PDFs |
| python-docx | pip package | ⚠️ If DOCX exists | Skip DOCX |
| openpyxl | pip package | ⚠️ If XLSX exists | Skip XLSX |
| python-pptx | pip package | ⚠️ If PPTX exists | Skip PPTX |
| pytesseract | pip package | ⚠️ If OCR needed | Skip OCR PDFs |
| sentence-transformers | pip package | ✅ Yes (primary) | BAAI/bge |
| url | Built-in | ✅ Yes | N/A |

### 6.3 Resource Requirements

| Resource | Minimum | Recommended | Scaling |
|----------|---------|-------------|---------|
| **CPU Cores** | 2 | 4+ | Linear |
| **RAM** | 4GB | 8GB | Linear with file count |
| **Disk Space** | 500MB | 2GB | Linear with file size |
| **Qdrant Memory** | 1GB | 2GB | Linear with vector count |

**Estimates for 10,000 files**:
- Average file size: 1MB
- Average chunks per file: 10
- Total chunks: 100,000
- Vector size: 384 floats × 4 bytes = 1.5KB per vector
- Total vector storage: ~150MB
- Total payload storage: ~500MB
- **Total**: ~650MB

### 6.4 Startup Sequence

```
1. Check Qdrant service is running:
   - Host: localhost
   - Port: 6333
   - Health check: GET http://localhost:6333/readyz

2. Load configuration from:
   - config.yaml
   - Environment variables (override)
   - Command-line arguments (override)

3. Initialize Vector Store:
   - Create collection 'rag_deductions' if not exists
   - Verify vector size matches model output

4. Load embedding model:
   - Try all-MiniLM-L6-v2
   - Fallback to BAAI/bge-small-en-v1.5
   - Lazy load on first use

5. Start processing:
   - Batch mode: iterate over base_path
   - Watch mode: start file watcher
```

### 6.5 Error Handling & Recovery

| Error Type | Recovery Strategy |
|------------|-------------------|
| Qdrant unavailable | Retry 3× with 5s delay, then fail |
| File read error | Skip file, log error, continue |
| Model load error | Try fallback, then fail |
| Embedding error | Skip chunk, log warning, continue |
| Deduction error | Skip chunk, log warning, continue |
| Comparison error | Skip comparison, log error, continue |

**Crash Recovery**:
- All state stored in Qdrant + JSONL files (durable)
- Re-running ingestion with same files → detects unchanged hashes → skips
- Incomplete files (from crash) → re-processed on next run

---

## 7. Key Design Trade-offs

### 7.1 Trade-off 1: Accuracy vs. Speed (Embedding Model)

| Option | Accuracy | Speed | Memory | Decision |
|--------|----------|-------|--------|----------|
| all-mpnet-base-v2 | ⭐⭐⭐⭐⭐ | ⭐⭐ | 420MB | ❌ Too large |
| all-MiniLM-L6-v2 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 80MB | ✅ **Chosen** |
| BAAI/bge-small | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 100MB | ✅ Fallback |
| Custom tiny model | ⭐⭐ | ⭐⭐⭐⭐⭐ | 10MB | ❌ Accuracy too low |

**Rationale**: all-MiniLM-L6-v2 provides excellent balance for development. Production can upgrade if needed.
**Impact**: Slightly lower accuracy than larger models, but acceptable for proof-of-concept.
**Mitigation**: Use table-based deduction for high-precision data (bypasses embedding accuracy).

---

### 7.2 Trade-off 2: Chunk Size vs. Context

| Chunk Size | Pros | Cons | Decision |
|------------|------|------|----------|
| 256 tokens | Fine-grained, precise retrieval | Loses context, more chunks | ❌ Too small |
| **512 tokens** | **Balanced context, good retrieval** | **Moderate chunk count** | ✅ **Chosen** |
| 1024 tokens | Full context, fewer chunks | Poor retrieval precision, expensive | ❌ Too large |

**Rationale**: 512 tokens is the "sweet spot" for most embedding models and retrieval tasks.
**Impact**: May miss very long-document context.
**Mitigation**: Use 20% overlap to preserve context across chunk boundaries.

---

### 7.3 Trade-off 3: Structured vs. Unstructured Deduction

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **Regex + Table Extraction** | Fast, deterministic, no LLM needed | Limited to known patterns | ✅ **Primary** |
| LLM-based Extraction | Handles novel patterns, high accuracy | Slow, requires LLM, non-deterministic | ⚠️ Future |
| Hybrid | Best of both | Complex implementation | ❌ Later phase |

**Rationale**: Regex + table extraction is sufficient forstructured data (invoices, reports) and fast for batch processing.
**Impact**: May miss complex relationships in unstructured text.
**Mitigation**: Include raw text in deductions for human review of ambiguous cases.

---

### 7.4 Trade-off 4: Qdrant vs. In-Memory Vector Store

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Qdrant** | Persistent, scalable, filterable, production-ready | External dependency | ✅ **Chosen** |
| FAISS | Fast, in-process | In-memory only, limited filtering | ❌ No persistence |
| Weaviate | Rich features, filtering | Heavier, new dependency | ❌ Not available |

**Rationale**: Qdrant is already available in the environment and provides all needed features.
**Impact**: Adds external service dependency.
**Mitigation**: Qdrant is lightweight; can run locally alongside Neo4j.

---

### 7.5 Trade-off 5: Full Independence vs. Timestamp Reuse

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Reuse extract.py** | Consistent timestamps with KG, proven code | Coupling to parent project | ✅ **Chosen** |
| Duplicate extract.py | Full isolation | Code duplication, maintenance burden | ❌ Worse |
| Custom implementation | Full control | Risk of inconsistency | ❌ Risky |

**Rationale**: `extract.py` only deals with file metadata, not KG. Reusing it ensures temporal consistency.
**Impact**: Coupling to parent project's file structure.
**Mitigation**: Isolate `extract.py` usage to a single wrapper class; document the dependency.

---

### 7.6 Trade-off 6: JSONL vs. Database for Deductions

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **JSONL** | Simple, human-readable, easy backup | No querying, slower for large datasets | ✅ **Primary** |
| SQLite | Queryable, fast, ACID | More complex, new dependency | ⚠️ Alternative |
| Qdrant Payload | Already stored, filterable | Harder to backup/export | ⚠️ Secondary |

**Rationale**: JSONL is simplest for persistence and human debugging. Qdrant payloads are used for retrieval.
**Impact**: Slower for large-scale comparison operations.
**Mitigation**: For production, can add SQLite as optional storage.

---

## 8. Summary

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Architecture** | Modular pipeline | Clean separation of concerns, testability |
| **Vector Store** | Qdrant | Available, persistent, filterable |
| **Embedding Model** | all-MiniLM-L6-v2 | Balanced accuracy/speed/size |
| **File Parsers** | Specialized libraries | Reliable extraction for each format |
| **Timestamp Source** | extract.py | Consistency with KG system |
| **Storage** | Qdrant + JSONL | Retrieval + persistence |
| **KG Independence** | Physical + dependency isolation | Guaranteed no KG access in RAG pipeline |
| **Configuration** | YAML + env vars | Flexibility without code changes |

---

## 9. Next Stage

**Awaiting human validation** of this architecture and design before proceeding to **Stage 5 – Planner** (`05_RAG_Task_Breakdown.md`).

---
**Status**: Draft awaiting explicit human approval
