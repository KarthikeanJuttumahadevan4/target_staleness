# 06_RAG_Tickets.md – Implementation Tickets

---

## 🔒 Gating Policy

The following **gating rules** apply to all tickets:

1. **P0 Gate**: ALL **Phase 1 P0** tickets must be **COMPLETED and APPROVED** before ANY **Phase 2** ticket may begin
2. **P1 Gate**: ALL **Phase 2 P0** tickets must be **COMPLETED and APPROVED** before ANY **Phase 3 P1** ticket may begin
3. **P2 Gate**: ALL **Phase 3 P1** tickets must be **COMPLETED and APPROVED** before ANY **Phase 4 P2** ticket may begin

**Within a phase**, tasks may be executed in parallel unless they have **explicit dependencies** listed in the ticket.

**Approval Requirement**: Each ticket requires **human approval** before the next dependent ticket can start, unless the dependency is within the same phase and role.

---

## 📌 Phase 1: Infrastructure & Core Pipeline (P0)
**Goal**: Independent RAG system ingests `samples5/`, chunks, embeds, indexes, and retrieves.
**Gating**: Must complete ALL Phase 1 tickets before starting Phase 2.

---

### 🛠️ Developer Tickets (Phase 1)

#### **DEV-P0-01: Create RAG_data Directory Structure**

**Priority:** P0

**Description:**
Create the complete directory structure for the Independent RAG System as specified in Section 7 of `04_RAG_Architecture.md`. This includes all `src/`, `tests/`, and supporting directories with appropriate `__init__.py` files.

**Acceptance Criteria:**
- [ ] `RAG_data/src/` exists with subdirectories: `ingestion/`, `chunking/`, `embedding/`, `retrieval/`, `deduction/`, `comparison/`, `resolution/`, `storage/`, `utils/`
- [ ] `RAG_data/tests/` exists with subdirectories: `unit/`, `integration/`, `data/`
- [ ] All Python directories contain `__init__.py` files (can be empty)
- [ ] Directory structure matches the architecture diagram exactly

**Dependencies:** None

**Owner:** Developer

---

#### **DEV-P0-02: Implement Configuration System**

**Priority:** P0

**Description:**
Implement the configuration loading system as specified in Section 2.2.2 of `03_RAG_Specifications.md` and Section 9 of `04_RAG_Architecture.md`. The system must support YAML configuration with environment variable overrides.

**Acceptance Criteria:**
- [ ] `RAG_data/src/config.py` implements `Config` class with all parameters
- [ ] `RAG_data/config.yaml` contains all default values from Section 9.1
- [ ] Environment variables override config values (e.g., `RAG_MODEL=BAAI/bge-small-en-v1.5`)
- [ ] Invalid configurations raise clear errors with helpful messages
- [ ] Configuration is validated on load (e.g., batch_size > 0, port in valid range)
- [ ] Unit tests verify config loading and validation

**Dependencies:** DEV-P0-01

**Owner:** Developer

---

#### **DEV-P0-03: Implement File Ingestor**

**Priority:** P0

**Description:**
Implement the `FileIngestor` class as specified in Section 2.1 and Section 2.2.1 of `03_RAG_Specifications.md`. This component is responsible for reading files from `samples5/`, calculating hashes, extracting timestamps via `extract.py`, and handling errors gracefully.

**Acceptance Criteria:**
- [ ] `RAG_data/src/ingestion/file_ingestor.py` implements full `FileIngestor` class
- [ ] Supports batch mode (`ingest_all()`) and single file mode (`ingest_one()`)
- [ ] Calculates SHA-256 hash for each file
- [ ] Extracts `as_of` timestamp using `extract.py` with fallback to `os.path.getmtime`
- [ ] Validates files (exists, readable, non-empty, correct extension)
- [ ] Tracks previously ingested files by hash to skip unchanged files
- [ ] Returns `IngestionResult` objects with all required fields
- [ ] Handles errors gracefully (returns error in result, does not crash)
- [ ] Supports all allowed extensions: `.txt`, `.pdf`, `.docx`, `.xlsx`, `.pptx`

**Dependencies:** DEV-P0-02

**Owner:** Developer

---

#### **DEV-P0-04: Implement Text Chunker**

**Priority:** P0

**Description:**
Implement the `TextChunker` class as specified in Section 2.2.2 of `03_RAG_Specifications.md` using Algorithm 4.2. This component splits raw text into semantic chunks with configurable overlap.

**Acceptance Criteria:**
- [ ] `RAG_data/src/chunking/text_chunkers.py` implements `TextChunker` class
- [ ] Tokenizes text and splits into chunks of configurable size (default: 512 tokens)
- [ ] Includes configurable overlap (default: 102 tokens = 20%) between chunks
- [ ] Merges small chunks (< min_chunk_size) with adjacent chunks
- [ ] Preserves all metadata from ingestion (file_path, file_hash, as_of)
- [ ] Assigns unique `chunk_id` to each chunk
- [ ] Tracks `chunk_index` and `total_chunks` for each file
- [ ] Records `start_offset` and `end_offset` in tokens
- [ ] Each chunk contains full context for standalone understanding

**Dependencies:** DEV-P0-02

**Owner:** Developer

---

#### **DEV-P0-05: Implement Table Chunker**

**Priority:** P0

**Description:**
Implement the `TableChunker` class as specified in Section 2.2.2 of `03_RAG_Specifications.md` using Algorithm 4.3. This component handles structured data from Excel and PDF tables.

**Acceptance Criteria:**
- [ ] `RAG_data/src/chunking/table_chunkers.py` implements `TableChunker` class
- [ ] Splits table data into row-based chunks
- [ ] Preserves column headers in metadata
- [ ] Each row becomes a separate chunk with metadata: `table_headers`, `row_number`
- [ ] Formats table rows as markdown tables (optional but recommended)
- [ ] Handles edge cases: empty rows, missing values, irregular tables
- [ ] Preserves all ingestion metadata
- [ ] Assigns unique `chunk_id` to each row chunk

**Dependencies:** DEV-P0-02

**Owner:** Developer

---

#### **DEV-P0-06: Implement Embedder**

**Priority:** P0

**Description:**
Implement the `Embedder` class as specified in Section 2.2.3 of `03_RAG_Specifications.md` and Section 3.2 of `04_RAG_Architecture.md`. This component generates embeddings using local sentence-transformers models.

**Acceptance Criteria:**
- [ ] `RAG_data/src/embedding/embedder.py` implements `Embedder` class
- [ ] Default model: `sentence-transformers/all-MiniLM-L6-v2`
- [ ] Fallback model: `BAAI/bge-small-en-v1.5`
- [ ] Implements `embed()` for batch embedding and `embed_single()` for one-off
- [ ] L2-normalizes embeddings before returning
- [ ] Supports configurable batch size (default: 32)
- [ ] Handles empty input lists gracefully
- [ ] Lazy loads model on first use (not at import time)
- [ ] Raises clear error if no model is available

**Dependencies:** DEV-P0-02

**Owner:** Developer

---

#### **DEV-P0-07: Implement Qdrant Client**

**Priority:** P0

**Description:**
Implement the `VectorSearcher` class (Qdrant client wrapper) as specified in Section 2.2.4 of `03_RAG_Specifications.md`. This component manages all interactions with the Qdrant vector store.

**Acceptance Criteria:**
- [ ] `RAG_data/src/storage/qdrant_client.py` implements `VectorSearcher` class
- [ ] Connects to Qdrant at `localhost:6333` (configurable)
- [ ] Creates collection `rag_deductions` with vector size 384 and Cosine distance
- [ ] Implements `initialize_collection()` to create/reconfigure collection
- [ ] Implements `index()` to add vectors with payloads
- [ ] Implements `search()` with configurable limit and filters
- [ ] Implements `delete_by_file()` to remove all entries for a file
- [ ] Handles connection errors gracefully (retries, clear error messages)
- [ ] Supports batch indexing for efficiency

**Dependencies:** DEV-P0-02

**Owner:** Developer

---

#### **DEV-P0-08: Implement Fact Deducer**

**Priority:** P0

**Description:**
Implement the `FactDeducer` class as specified in Section 2.2.5 of `03_RAG_Specifications.md` using Algorithm 4.5. This component extracts structured facts from chunks using regex patterns and table data.

**Acceptance Criteria:**
- [ ] `RAG_data/src/deduction/fact_deducer.py` implements `FactDeducer` class
- [ ] Extracts facts using regex patterns (see predicate map in Section 9.1)
- [ ] Handles table-based extraction with higher confidence (0.98 vs 0.95 for regex)
- [ ] Implements `deduct()` for single chunk and `deduct_batch()` for multiple
- [ ] Normalizes values (strip whitespace, lowercase text, extract numbers)
- [ ] Maps natural language to standard predicates (e.g., "price" → "has_price")
- [ ] Calculates confidence scores for each deduction
- [ ] Preserves provenance with extraction method and raw text
- [ ] Returns `RAGDeduction` objects with all required fields
- [ ] Handles extraction failures gracefully (returns empty list, not error)

**Dependencies:** DEV-P0-04, DEV-P0-05

**Owner:** Developer

---

#### **DEV-P0-09: Implement JSONL Storage**

**Priority:** P0

**Description:**
Implement persistent storage for RAG deductions using JSON Lines format as specified in Section 2.2.5 of `03_RAG_Specifications.md`.

**Acceptance Criteria:**
- [ ] `RAG_data/src/storage/jsonl_store.py` implements JSONL storage
- [ ] Implements `read_deductions()` to load all deductions from `deductions.jsonl`
- [ ] Implements `write_deduction()` to append a single deduction
- [ ] Implements `write_deductions()` to append multiple deductions
- [ ] File path: `RAG_data/deductions.jsonl`
- [ ] Handles file I/O errors gracefully
- [ ] Supports reading partial files (for crash recovery)
- [ ] Each line is a valid JSON object (one deduction per line)

**Dependencies:** DEV-P0-02

**Owner:** Developer

---

#### **DEV-P0-10: Implement Pipeline Orchestration**

**Priority:** P0

**Description:**
Create the main pipeline script that orchestrates the entire ingestion workflow: file ingestion → chunking → embedding → fact deduction → storage. This is the primary entry point for the Independent RAG System.

**Acceptance Criteria:**
- [ ] `RAG_data/ingest_pipeline.py` implements the main CLI script
- [ ] Supports `--batch` mode for full ingestion of `samples5/`
- [ ] Supports `--watch` mode for incremental updates
- [ ] Integrates all components: FileIngestor, TextChunker, TableChunker, Embedder, VectorSearcher, FactDeducer, JSONLStore
- [ ] Accepts `--config` argument to specify config file
- [ ] Logs progress and errors to console
- [ ] Handles all file types in `samples5/`
- [ ] Skips unchanged files based on hash comparison
- [ ] Returns success/failure status

**Dependencies:** DEV-P0-03, DEV-P0-04, DEV-P0-05, DEV-P0-06, DEV-P0-07, DEV-P0-08, DEV-P0-09

**Owner:** Developer

---

### 🧪 Tester Tickets (Phase 1)

#### **TEST-P0-01: Unit Tests for File Ingestor**

**Priority:** P0

**Description:**
Write comprehensive unit tests for the `FileIngestor` class. Tests must cover normal cases, edge cases, and error handling.

**Acceptance Criteria:**
- [ ] Test ingestion of each file type: `.txt`, `.pdf`, `.docx`, `.xlsx`, `.pptx`
- [ ] Test SHA-256 hash calculation
- [ ] Test timestamp extraction (both extract.py success and fallback)
- [ ] Test file validation (empty file, invalid extension, missing file)
- [ ] Test skipped files (unchanged hash)
- [ ] Test error handling (permission denied, corrupt file)
- [ ] Achieve ≥80% code coverage of `file_ingestor.py`
- [ ] Tests run in < 10 seconds

**Dependencies:** DEV-P0-03

**Owner:** Tester

---

#### **TEST-P0-02: Unit Tests for Text Chunker**

**Priority:** P0

**Description:**
Write comprehensive unit tests for the `TextChunker` class.

**Acceptance Criteria:**
- [ ] Test chunking with default parameters (512 tokens, 102 overlap)
- [ ] Test chunking with custom parameters
- [ ] Test chunk size is ≤ max_chunk_size
- [ ] Test overlap between consecutive chunks
- [ ] Test small chunks are merged (< min_chunk_size)
- [ ] Test metadata preservation (file_path, file_hash, as_of)
- [ ] Test chunk IDs are unique
- [ ] Test empty text handling
- [ ] Achieve ≥80% code coverage of `text_chunkers.py`

**Dependencies:** DEV-P0-04

**Owner:** Tester

---

#### **TEST-P0-03: Unit Tests for Embedder**

**Priority:** P0

**Description:**
Write comprehensive unit tests for the `Embedder` class.

**Acceptance Criteria:**
- [ ] Test embedding generation for single text
- [ ] Test batch embedding for multiple texts
- [ ] Test embeddings are L2-normalized
- [ ] Test embedding dimension matches model output (384 or 512)
- [ ] Test empty input list handling
- [ ] Test model fallback (if primary model unavailable)
- [ ] Test lazy loading (model not loaded until first embed call)
- [ ] Achieve ≥80% code coverage of `embedder.py`

**Dependencies:** DEV-P0-06

**Owner:** Tester

---

#### **TEST-P0-04: Unit Tests for Qdrant Client**

**Priority:** P0

**Description:**
Write comprehensive unit tests for the `VectorSearcher` (Qdrant client) class.

**Acceptance Criteria:**
- [ ] Test collection initialization
- [ ] Test indexing single vector with payload
- [ ] Test batch indexing multiple vectors
- [ ] Test search returns correct results
- [ ] Test search with limit parameter
- [ ] Test search with filters (e.g., file_path)
- [ ] Test delete_by_file removes correct entries
- [ ] Test error handling for connection failures
- [ ] Achieve ≥80% code coverage of `qdrant_client.py`

**Dependencies:** DEV-P0-07

**Owner:** Tester

---

#### **TEST-P0-05: Unit Tests for Fact Deducer**

**Priority:** P0

**Description:**
Write comprehensive unit tests for the `FactDeducer` class.

**Acceptance Criteria:**
- [ ] Test fact extraction from text with regex patterns
- [ ] Test fact extraction from table data
- [ ] Test predicate mapping (e.g., "price" → "has_price")
- [ ] Test value normalization (numbers, dates, text)
- [ ] Test confidence score calculation
- [ ] Test provenance tracking
- [ ] Test extraction from chunks with no matches (returns empty list)
- [ ] Test handling of various number formats ($100, 100, 100.00)
- [ ] Achieve ≥80% code coverage of `fact_deducer.py`

**Dependencies:** DEV-P0-08

**Owner:** Tester

---

#### **TEST-P0-06: Integration Test – Full Pipeline**

**Priority:** P0

**Description:**
Write an end-to-end integration test that runs the complete ingestion pipeline on a set of test files and verifies correct behavior.

**Acceptance Criteria:**
- [ ] Test files exist in `RAG_data/tests/data/sample_files/`
- [ ] Test files include: `.txt`, `.pdf`, `.xlsx` (minimum)
- [ ] Run `python ingest_pipeline.py --batch` on test directory
- [ ] Verify all files are ingested successfully
- [ ] Verify chunks are created for each file
- [ ] Verify embeddings are generated and indexed in Qdrant
- [ ] Verify deductions are written to `deductions.jsonl`
- [ ] Verify deductions contain expected facts (e.g., price extraction)
- [ ] Verify no errors are logged

**Dependencies:** DEV-P0-10

**Owner:** Tester

---

### 👀 Reviewer Tickets (Phase 1)

#### **REV-P0-01: Code Review – Infrastructure**

**Priority:** P0

**Description:**
Review all infrastructure code: directory structure, configuration system, file ingestor, chunkers.

**Acceptance Criteria:**
- [ ] Verify directory structure matches architecture
- [ ] Verify config system is complete and functional
- [ ] Verify file ingestor handles all file types
- [ ] Verify text and table chunkers produce correct chunks
- [ ] Verify no KG dependencies (no imports from `src/temporal/`, `src/ingestion/`, `src/indexing/`)
- [ ] Verify error handling is comprehensive
- [ ] Approve or request changes

**Dependencies:** DEV-P0-01, DEV-P0-02, DEV-P0-03, DEV-P0-04, DEV-P0-05

**Owner:** Reviewer

---

#### **REV-P0-02: Code Review – Embedding & Storage**

**Priority:** P0

**Description:**
Review embedding, Qdrant client, fact deducer, and JSONL storage components.

**Acceptance Criteria:**
- [ ] Verify embedder correctly implements model loading and embedding
- [ ] Verify Qdrant client handles all operations correctly
- [ ] Verify fact deducer extracts facts accurately
- [ ] Verify JSONL storage is reliable and persistent
- [ ] Verify no KG dependencies
- [ ] Verify proper error handling
- [ ] Approve or request changes

**Dependencies:** DEV-P0-06, DEV-P0-07, DEV-P0-08, DEV-P0-09

**Owner:** Reviewer

---

#### **REV-P0-03: Code Review – Pipeline Orchestration**

**Priority:** P0

**Description:**
Review the main pipeline script and its integration of all components.

**Acceptance Criteria:**
- [ ] Verify pipeline script correctly orchestrates all components
- [ ] Verify batch mode works correctly
- [ ] Verify watch mode is implemented (if applicable in Phase 1)
- [ ] Verify CLI arguments are handled properly
- [ ] Verify logging is informative
- [ ] Verify no KG dependencies
- [ ] Approve or request changes

**Dependencies:** DEV-P0-10

**Owner:** Reviewer

---

#### **REV-P0-04: Architecture Validation**

**Priority:** P0

**Description:**
Validate that the implemented system matches the approved architecture in `04_RAG_Architecture.md`.

**Acceptance Criteria:**
- [ ] Verify all technology choices are implemented (Qdrant, sentence-transformers, etc.)
- [ ] Verify data flow matches the architecture diagram
- [ ] Verify all components are present and functional
- [ ] Verify independence from KG is maintained
- [ ] Verify configuration system is complete
- [ ] Approve or request architectural changes

**Dependencies:** REV-P0-01, REV-P0-02, REV-P0-03

**Owner:** Reviewer

---

## 📌 Phase 2: Comparison Module (P0)
**Goal**: System can compare RAG deductions with KG facts and detect/resolve inconsistencies.
**Gating**: Must complete ALL Phase 1 tickets before starting Phase 2. Must complete ALL Phase 2 tickets before starting Phase 3.

---

### 🛠️ Developer Tickets (Phase 2)

#### **DEV-P0-11: Implement Aligner**

**Priority:** P0

**Description:**
Implement the `Aligner` class as specified in Section 2.2.6 of `03_RAG_Specifications.md` using Algorithm 6.1. This component matches RAG deductions with KG facts.

**Acceptance Criteria:**
- [ ] `RAG_data/src/comparison/aligner.py` implements `Aligner` class
- [ ] Implements exact matching by (subject_entity, predicate, source_file_path)
- [ ] Implements fuzzy matching by (subject_entity, predicate) with configurable confidence threshold
- [ ] Implements semantic matching using embeddings with configurable similarity threshold
- [ ] Implements multi-match handling (prefer matching source_file_path, then current=true, then newest as_of)
- [ ] Returns `Alignment` objects with alignment_type and confidence
- [ ] Handles cases where no match is found
- [ ] Configurable thresholds for fuzzy and semantic matching

**Dependencies:** DEV-P0-08 (Fact Deducer for RAG deductions schema)

**Owner:** Developer

---

#### **DEV-P0-12: Implement Inconsistency Detector**

**Priority:** P0

**Description:**
Implement the `InconsistencyDetector` class as specified in Section 2.2.7 of `03_RAG_Specifications.md` using Algorithm 6.2. This component identifies inconsistencies between aligned deductions and facts.

**Acceptance Criteria:**
- [ ] `RAG_data/src/comparison/detectors.py` implements `InconsistencyDetector` class
- [ ] Detects all inconsistency types: Value Conflict, RAG Missing, KG Missing, Temporal Conflict, Type Mismatch, Interpretation Conflict
- [ ] Classifies severity (HIGH, MEDIUM, LOW) for each inconsistency
- [ ] Handles cases where only RAG or only KG has data
- [ ] Normalizes values before comparison
- [ ] Returns `Inconsistency` objects with all required fields
- [ ] Groups inconsistencies by subject_entity + predicate

**Dependencies:** DEV-P0-11

**Owner:** Developer

---

#### **DEV-P0-13: Implement Resolver**

**Priority:** P0

**Description:**
Implement the `Resolver` class as specified in Section 2.2.8 of `03_RAG_Specifications.md` using Algorithm 6.3. This component applies automatic resolution rules or escalates to human.

**Acceptance Criteria:**
- [ ] `RAG_data/src/resolution/resolver.py` implements `Resolver` class
- [ ] Implements all 7 resolution rules (R1-R7) from Section 5.1
- [ ] Rules are applied in correct priority order
- [ ] Returns `ResolutionResult` with rule_applied, action, and resolved flag
- [ ] Raises `HumanEscalationError` when no rule matches (signals need for human report)
- [ ] Handles all inconsistency types correctly
- [ ] Logs all resolutions to `resolution_log.jsonl`

**Dependencies:** DEV-P0-12

**Owner:** Developer

---

#### **DEV-P0-14: Implement Reporter**

**Priority:** P0

**Description:**
Implement the reporting functionality as specified in Section 2.2.9 and Section 5.3 of `03_RAG_Specifications.md`.

**Acceptance Criteria:**
- [ ] `RAG_data/src/resolution/reports.py` implements report generation functions
- [ ] Implements `generate_escalation_report()` function
- [ ] Reports include all required sections from Section 5.3:
  - Summary (status, reported at, severity)
  - Conflict Details (type, entity, predicate)
  - RAG Deduction details
  - KG Fact details
  - Resolution Attempt (rules applied, blocking rule)
  - Recommended Action (options with pros/cons)
  - Human Decision section (for manual review)
- [ ] Reports are serializable to markdown and JSON
- [ ] Implements `log_resolution()` to append to `resolution_log.jsonl`

**Dependencies:** DEV-P0-13

**Owner:** Developer

---

#### **DEV-P0-15: Implement KG Fact Fetcher**

**Priority:** P0

**Description:**
Implement a utility to fetch facts from the Knowledge Graph via Neo4j. This is the **only** component that accesses the KG, and it is used solely for comparison purposes.

**Acceptance Criteria:**
- [ ] `RAG_data/src/comparison/kg_fetcher.py` implements KG fact retrieval
- [ ] Connects to Neo4j at `bolt://localhost:7687` with credentials
- [ ] Queries for facts by entity, predicate, or full scan
- [ ] Converts Neo4j results to `KGFact` objects
- [ ] Handles connection errors gracefully (retries, clear messages)
- [ ] **READ-ONLY**: Never writes to KG, only reads
- [ ] Includes timeout for queries

**Dependencies:** Phase 1 complete (to ensure independence)

**Owner:** Developer

---

#### **DEV-P0-16: Implement Comparison Script**

**Priority:** P0

**Description:**
Create the main comparison script that orchestrates the comparison workflow: fetch KG facts → load RAG deductions → align → detect inconsistencies → resolve → report.

**Acceptance Criteria:**
- [ ] `RAG_data/compare.py` implements the main CLI script
- [ ] Loads RAG deductions from `deductions.jsonl`
- [ ] Fetches KG facts using KG Fact Fetcher
- [ ] Orchestrates alignment using Aligner
- [ ] Detects inconsistencies using InconsistencyDetector
- [ ] Resolves inconsistencies using Resolver
- [ ] Generates reports for unresolved inconsistencies
- [ ] Supports `--output` argument to specify report directory
- [ ] Logs progress and results

**Dependencies:** DEV-P0-11, DEV-P0-12, DEV-P0-13, DEV-P0-14, DEV-P0-15

**Owner:** Developer

---

### 🧪 Tester Tickets (Phase 2)

#### **TEST-P0-07: Unit Tests for Aligner**

**Priority:** P0

**Description:**
Write comprehensive unit tests for the `Aligner` class.

**Acceptance Criteria:**
- [ ] Test exact matching with same (subject_entity, predicate, source_file_path)
- [ ] Test fuzzy matching with configurable confidence threshold
- [ ] Test semantic matching with configurable similarity threshold
- [ ] Test preference ordering (matching source > current > newest as_of)
- [ ] Test handling of multiple matches
- [ ] Test handling of no matches
- [ ] Test edge cases (empty inputs, null values)
- [ ] Achieve ≥80% code coverage of `aligner.py`

**Dependencies:** DEV-P0-11

**Owner:** Tester

---

#### **TEST-P0-08: Unit Tests for Inconsistency Detector**

**Priority:** P0

**Description:**
Write comprehensive unit tests for the `InconsistencyDetector` class.

**Acceptance Criteria:**
- [ ] Test detection of Value Conflict
- [ ] Test detection of RAG Missing
- [ ] Test detection of KG Missing
- [ ] Test detection of Temporal Conflict
- [ ] Test detection of Type Mismatch
- [ ] Test detection of Interpretation Conflict
- [ ] Test severity classification for each type
- [ ] Test grouping by subject_entity + predicate
- [ ] Test edge cases (null values, empty fields)
- [ ] Achieve ≥80% code coverage of `detectors.py`

**Dependencies:** DEV-P0-12

**Owner:** Tester

---

#### **TEST-P0-09: Unit Tests for Resolver**

**Priority:** P0

**Description:**
Write comprehensive unit tests for the `Resolver` class.

**Acceptance Criteria:**
- [ ] Test application of rule R1 (exact match)
- [ ] Test application of rule R2 (prefer newer RAG)
- [ ] Test application of rule R3 (prefer newer KG)
- [ ] Test application of rule R4 (structured > unstructured)
- [ ] Test application of rule R5 (KG provenance chain)
- [ ] Test application of rule R6 (numeric > text)
- [ ] Test application of rule R7 (ISO date > natural text)
- [ ] Test correct priority ordering (R2 before R4, etc.)
- [ ] Test human escalation is triggered when no rule matches
- [ ] Test resolution logging to `resolution_log.jsonl`
- [ ] Achieve ≥80% code coverage of `resolver.py`

**Dependencies:** DEV-P0-13

**Owner:** Tester

---

#### **TEST-P0-10: Unit Tests for Reporter**

**Priority:** P0

**Description:**
Write comprehensive unit tests for the reporting functionality.

**Acceptance Criteria:**
- [ ] Test report generation for Value Conflict
- [ ] Test report generation for RAG Missing
- [ ] Test report generation for KG Missing
- [ ] Test report generation for Temporal Conflict
- [ ] Test report contains all required sections
- [ ] Test markdown formatting of reports
- [ ] Test JSON serialization of reports
- [ ] Test resolution logging
- [ ] Achieve ≥80% code coverage of `reports.py`

**Dependencies:** DEV-P0-14

**Owner:** Tester

---

#### **TEST-P0-11: Integration Test – Full Comparison**

**Priority:** P0

**Description:**
Write an end-to-end integration test that runs the complete comparison workflow with intentionally planted inconsistencies.

**Acceptance Criteria:**
- [ ] Create test dataset with known inconsistencies:
  - At least 3 Value Conflicts
  - At least 2 RAG Missing facts
  - At least 2 KG Missing facts
  - At least 1 Temporal Conflict
- [ ] Run `python ingest_pipeline.py --batch` to generate RAG deductions
- [ ] Ensure KG has corresponding facts (manually inserted for test)
- [ ] Run `python compare.py` to detect inconsistencies
- [ ] Verify ≥90% of planted inconsistencies are detected
- [ ] Verify ≥80% of detected inconsistencies are auto-resolved
- [ ] Verify human escalation reports are generated for unresolved inconsistencies

**Dependencies:** DEV-P0-16

**Owner:** Tester

---

### 👀 Reviewer Tickets (Phase 2)

#### **REV-P0-05: Code Review – Comparison Components**

**Priority:** P0

**Description:**
Review all comparison module components: Aligner, InconsistencyDetector, Resolver, Reporter, KG Fact Fetcher.

**Acceptance Criteria:**
- [ ] Verify Aligner correctly matches deductions to facts
- [ ] Verify Detector correctly identifies all inconsistency types
- [ ] Verify Resolver correctly applies all rules in priority order
- [ ] Verify Reporter generates proper escalation reports
- [ ] Verify KG Fact Fetcher is read-only
- [ ] Verify no KG dependencies in RAG pipeline code
- [ ] Approve or request changes

**Dependencies:** DEV-P0-11, DEV-P0-12, DEV-P0-13, DEV-P0-14, DEV-P0-15

**Owner:** Reviewer

---

#### **REV-P0-06: Test Review – Comparison Module**

**Priority:** P0

**Description:**
Review all comparison module tests for completeness and correctness.

**Acceptance Criteria:**
- [ ] Verify TEST-P0-07 covers all alignment scenarios
- [ ] Verify TEST-P0-08 covers all inconsistency types
- [ ] Verify TEST-P0-09 covers all resolution rules
- [ ] Verify TEST-P0-10 covers report generation
- [ ] Verify TEST-P0-11 validates detection and resolution rates
- [ ] Verify tests meet ≥80% coverage targets
- [ ] Approve or request additional tests

**Dependencies:** TEST-P0-07, TEST-P0-08, TEST-P0-09, TEST-P0-10, TEST-P0-11

**Owner:** Reviewer

---

#### **REV-P0-07: Independence Audit**

**Priority:** P0

**Description:**
Perform a thorough audit to verify the Independent RAG System has **zero dependencies** on the Knowledge Graph, except for the explicit read-only comparison.

**Acceptance Criteria:**
- [ ] Run `grep -r "from temporal" RAG_data/src/` – must return **no results**
- [ ] Run `grep -r "from ingestion" RAG_data/src/` – must return **no results**
- [ ] Run `grep -r "from indexing" RAG_data/src/` – must return **no results**
- [ ] Run `grep -r "neo4j" RAG_data/src/` – must return **no results** (except in kg_fetcher.py)
- [ ] Verify only `kg_fetcher.py` imports Neo4j code
- [ ] Verify RAG pipeline scripts (ingest_pipeline.py) do not import KG modules
- [ ] Verify all imports are from standard library or external packages
- [ ] Approve or block release

**Dependencies:** All Phase 1 and Phase 2 Developer tasks

**Owner:** Reviewer

---

## 📌 Phase 3: Quality Assurance & Hardening (P1)
**Goal**: System is robust, well-tested, and production-ready.
**Gating**: Must complete ALL Phase 2 tickets before starting Phase 3. Must complete ALL Phase 3 tickets before starting Phase 4.

---

### 🛠️ Developer Tickets (Phase 3)

#### **DEV-P1-17: Add Incremental File Watcher**

**Priority:** P1

**Description:**
Add file system watching capability to the ingestion pipeline, allowing it to process new or modified files automatically.

**Acceptance Criteria:**
- [ ] Implement `FileWatcher` class using `watchdog` library
- [ ] Start watcher with `python ingest_pipeline.py --watch`
- [ ] Watcher monitors `samples5/` directory for file changes
- [ ] On CREATE or MODIFY events, triggers ingestion of affected file
- [ ] On DELETE events, removes file entries from Qdrant and deductions.jsonl
- [ ] Handles rapid file changes gracefully
- [ ] Provides console output for watcher events

**Dependencies:** DEV-P0-03, DEV-P0-10

**Owner:** Developer

---

#### **DEV-P1-18: Add Structured Logging**

**Priority:** P1

**Description:**
Implement structured logging across all components for better debugging and monitoring.

**Acceptance Criteria:**
- [ ] Add logging configuration to `config.py`
- [ ] All modules use `logging` module (not print statements)
- [ ] Log levels configurable: DEBUG, INFO, WARNING, ERROR
- [ ] Logs to console and file (`RAG_data/logs/rag.log`)
- [ ] Log format includes: timestamp, level, module, message
- [ ] Critical operations logged at INFO level
- [ ] Errors logged at ERROR level with full stack trace
- [ ] Performance metrics logged at DEBUG level

**Dependencies:** DEV-P0-02

**Owner:** Developer

---

#### **DEV-P1-19: Add Metrics Collection**

**Priority:** P1

**Description:**
Add metrics collection to track system performance and throughput.

**Acceptance Criteria:**
- [ ] Track metrics: files processed, chunks created, deductions extracted, time taken
- [ ] Metrics stored in-memory and optionally logged
- [ ] End-to-end timing for ingestion pipeline
- [ ] Per-file timing breakdown
- [ ] Metrics summary printed at end of batch ingestion
- [ ] Metrics include: total time, files/sec, chunks/sec

**Dependencies:** Phase 1 complete

**Owner:** Developer

---

#### **DEV-P1-20: Add CLI Arguments**

**Priority:** P1

**Description:**
Add command-line argument parsing to all scripts using `argparse`.

**Acceptance Criteria:**
- [ ] `ingest_pipeline.py` accepts: `--batch`, `--watch`, `--config`, `--base-path`, `--help`
- [ ] `compare.py` accepts: `--output`, `--config`, `--help`
- [ ] All arguments have help text and sensible defaults
- [ ] Config file path can be specified via CLI
- [ ] Invalid arguments produce clear error messages
- [ ] `--help` displays all options

**Dependencies:** Phase 1 complete

**Owner:** Developer

---

#### **DEV-P1-21: Add Input Validation**

**Priority:** P1

**Description:**
Add validation for all inputs (file paths, configuration values, etc.).

**Acceptance Criteria:**
- [ ] Validate file paths exist and are readable
- [ ] Validate configuration values are in valid ranges
- [ ] Validate chunk_size > 0 and <= 1024
- [ ] Validate overlap < chunk_size
- [ ] Validate confidence_threshold between 0.0 and 1.0
- [ ] Validate Qdrant host/port are reachable
- [ ] Clear error messages for all validation failures

**Dependencies:** Phase 1 complete

**Owner:** Developer

---

#### **DEV-P1-22: Add Retry Logic**

**Priority:** P1

**Description:**
Add retry logic for transient failures (e.g., Qdrant temporary unavailability).

**Acceptance Criteria:**
- [ ] Configurable retry count (default: 3)
- [ ] Configurable retry delay (default: 5 seconds)
- [ ] Exponential backoff for retries
- [ ] Retry on Qdrant connection errors
- [ ] Retry on file read errors (temporary locks)
- [ ] No retry on permanent errors (invalid data)
- [ ] Logs retry attempts with attempt number

**Dependencies:** Phase 1 complete

**Owner:** Developer

---

#### **DEV-P1-23: Add OCR Support for Scanned PDFs**

**Priority:** P1

**Description:**
Add OCR capability to extract text from scanned PDFs and image-based documents.

**Acceptance Criteria:**
- [ ] Detect when PDF cannot be parsed by pdfplumber (likely scanned)
- [ ] Fall back to OCR using `pdf2image` + `pytesseract`
- [ ] Convert PDF pages to images using `pdf2image`
- [ ] Extract text from images using `pytesseract`
- [ ] Handle OCR errors gracefully
- [ ] OCR text stored with `extraction_path: "ocr"`
- [ ] Works for both scanned PDFs and image-only documents

**Dependencies:** DEV-P0-03

**Owner:** Developer

---

### 🧪 Tester Tickets (Phase 3)

#### **TEST-P1-12: Integration Test – Incremental Updates**

**Priority:** P1

**Description:**
Test the incremental file watcher with file modifications.

**Acceptance Criteria:**
- [ ] Start watcher with `python ingest_pipeline.py --watch`
- [ ] Add new file to `samples5/` – verify it is ingested
- [ ] Modify existing file in `samples5/` – verify it is re-ingested
- [ ] Delete file from `samples5/` – verify entries are removed from Qdrant
- [ ] Verify hash comparison prevents unnecessary re-processing
- [ ] Verify watcher handles rapid file changes
- [ ] Verify watcher logs events correctly

**Dependencies:** DEV-P1-17

**Owner:** Tester

---

#### **TEST-P1-13: Performance Test – Ingestion Throughput**

**Priority:** P1

**Description:**
Measure and verify ingestion throughput meets targets.

**Acceptance Criteria:**
- [ ] Create test dataset with 1000+ files
- [ ] Run `python ingest_pipeline.py --batch`
- [ ] Measure total time and files/second
- [ ] Verify ≥100 files/minute throughput
- [ ] Verify memory usage ≤4GB
- [ ] Document results in test report

**Dependencies:** Phase 1 complete

**Owner:** Tester

---

#### **TEST-P1-14: Performance Test – Query Latency**

**Priority:** P1

**Description:**
Measure and verify query latency meets targets.

**Acceptance Criteria:**
- [ ] Index 10,000+ chunks in Qdrant
- [ ] Run 100 queries with various search terms
- [ ] Measure P50, P95, P99 latency
- [ ] Verify P95 latency ≤200ms
- [ ] Document results in test report

**Dependencies:** Phase 1 complete

**Owner:** Tester

---

#### **TEST-P1-15: Error Handling Test**

**Priority:** P1

**Description:**
Test system behavior with various error conditions.

**Acceptance Criteria:**
- [ ] Test with malformed files (invalid PDF, corrupt XLSX)
- [ ] Test with permission denied errors
- [ ] Test with Qdrant service unavailable
- [ ] Test with empty files
- [ ] Test with very large files (>100MB)
- [ ] Verify system handles all errors gracefully (no crashes)
- [ ] Verify appropriate error messages are logged
- [ ] Verify partial failures don't affect other files

**Dependencies:** Phase 1 complete

**Owner:** Tester

---

#### **TEST-P1-16: OCR Test**

**Priority:** P1

**Description:**
Test OCR functionality with scanned PDFs.

**Acceptance Criteria:**
- [ ] Create test scanned PDF (image-based, not text-based)
- [ ] Run ingestion with OCR support
- [ ] Verify PDF is detected as scanned
- [ ] Verify OCR extracts text successfully
- [ ] Verify text is chunked and indexed
- [ ] Verify facts are extracted from OCR text
- [ ] Verify extraction_path = "ocr" in metadata

**Dependencies:** DEV-P1-23

**Owner:** Tester

---

#### **TEST-P1-17: End-to-End Consistency Test**

**Priority:** P1

**Description:**
Comprehensive test verifying the entire system produces consistent, correct results.

**Acceptance Criteria:**
- [ ] Create comprehensive test dataset with:
  - Multiple file types
  - Known facts (prices, dates, headcounts)
  - Multiple versions of same entity
- [ ] Run full ingestion pipeline
- [ ] Verify all expected facts are extracted
- [ ] Verify facts have correct values and metadata
- [ ] Verify deductions are stored correctly
- [ ] Run comparison with KG facts
- [ ] Verify inconsistencies are detected correctly
- [ ] Verify auto-resolution works correctly

**Dependencies:** Phase 1 and Phase 2 complete

**Owner:** Tester

---

### 👀 Reviewer Tickets (Phase 3)

#### **REV-P1-08: Code Review – Enhancements**

**Priority:** P1

**Description:**
Review all Phase 3 developer enhancements.

**Acceptance Criteria:**
- [ ] Verify file watcher works correctly
- [ ] Verify logging is comprehensive and configurable
- [ ] Verify metrics collection is accurate
- [ ] Verify CLI arguments are user-friendly
- [ ] Verify input validation catches edge cases
- [ ] Verify retry logic handles transient failures
- [ ] Verify OCR support works with scanned PDFs
- [ ] Approve or request changes

**Dependencies:** DEV-P1-17 through DEV-P1-23

**Owner:** Reviewer

---

#### **REV-P1-09: Performance Review**

**Priority:** P1

**Description:**
Review performance test results and verify all targets are met.

**Acceptance Criteria:**
- [ ] Review TEST-P1-13 results (ingestion throughput ≥100 files/min)
- [ ] Review TEST-P1-14 results (P95 latency ≤200ms)
- [ ] Review resource usage (memory ≤4GB)
- [ ] Verify all performance criteria from Section 6.1 are met
- [ ] Approve or request optimizations

**Dependencies:** TEST-P1-13, TEST-P1-14

**Owner:** Reviewer

---

#### **REV-P1-10: Final Architecture Review**

**Priority:** P1

**Description:**
Perform final review of the entire system architecture and implementation.

**Acceptance Criteria:**
- [ ] Verify all components match the approved architecture
- [ ] Verify all specifications from 03_RAG_Specifications.md are implemented
- [ ] Verify all requirements from 02_RAG_Requirements_Analysis.md are met
- [ ] Verify all technical decisions from 04_RAG_Architecture.md are followed
- [ ] Verify system is production-ready
- [ ] Approve for final handoff

**Dependencies:** All Phase 1, 2, and 3 tasks

**Owner:** Reviewer

---

## 📌 Phase 4: Documentation & Polish (P2)
**Goal**: System is fully documented and ready for handoff.
**Gating**: Must complete ALL Phase 3 tickets before starting Phase 4.

---

### 🛠️ Developer Tickets (Phase 4)

#### **DEV-P2-24: Add Module Docstrings**

**Priority:** P2

**Description:**
Add Google-style docstrings to all public functions and classes.

**Acceptance Criteria:**
- [ ] All modules have module-level docstrings
- [ ] All public classes have class-level docstrings
- [ ] All public functions have function-level docstrings
- [ ] Docstrings follow Google style guide
- [ ] Docstrings include: description, args, returns, raises (where applicable)

**Dependencies:** All previous Developer tasks

**Owner:** Developer

---

#### **DEV-P2-25: Write README.md**

**Priority:** P2

**Description:**
Create comprehensive README for the Independent RAG System.

**Acceptance Criteria:**
- [ ] `RAG_data/README.md` exists
- [ ] Includes: Overview, Architecture, Setup, Usage, Configuration, Examples
- [ ] Setup section documents: Python version, dependencies, Qdrant setup
- [ ] Usage section documents: Ingestion, Comparison, Common commands
- [ ] Configuration section references config.yaml
- [ ] Examples section shows sample queries and outputs
- [ ] Includes troubleshooting guide

**Dependencies:** All previous Developer tasks

**Owner:** Developer

---

#### **DEV-P2-26: Write Development Guide**

**Priority:** P2

**Description:**
Create a development guide for contributors.

**Acceptance Criteria:**
- [ ] `RAG_data/DEVELOPMENT.md` exists
- [ ] Includes: Coding standards, Testing, Documentation, Deployment
- [ ] Coding standards cover: PEP 8, type hints, docstrings
- [ ] Testing section covers: Unit tests, Integration tests, Running tests
- [ ] Documentation section covers: Docstring style, Markdown format
- [ ] Deployment section covers: Dependencies, Configuration, Running

**Dependencies:** All previous Developer tasks

**Owner:** Developer

---

#### **DEV-P2-27: Add Type Stubs**

**Priority:** P2

**Description:**
Add `.pyi` stub files for better IDE support.

**Acceptance Criteria:**
- [ ] Type stubs for all public modules
- [ ] Stubs match actual implementation
- [ ] IDE autocomplete works for all public functions
- [ ] Type checking passes (mypy orpyright)

**Dependencies:** All previous Developer tasks

**Owner:** Developer

---

#### **DEV-P2-28: Create Example Files**

**Priority:** P2

**Description:**
Create example files in `samples5/` that demonstrate all file types and showcase the system's capabilities.

**Acceptance Criteria:**
- [ ] At least 5 example files covering all supported types:
  - `.txt` (plain text)
  - `.pdf` (text-based)
  - `.pdf` (scanned/OCR)
  - `.docx` (Word document)
  - `.xlsx` (Excel spreadsheet)
  - `.pptx` (PowerPoint)
- [ ] Each file contains realistic content with extractable facts
- [ ] Files have diverse modification timestamps for temporal testing
- [ ] Files are well-documented in `RAG_data/examples/README.md`

**Dependencies:** None (can be done in parallel with other Phase 4 tasks)

**Owner:** Developer

---

### 🧪 Tester Tickets (Phase 4)

#### **TEST-P2-18: Manual Testing – Demo Walkthrough**

**Priority:** P2

**Description:**
Document a complete demo walkthrough showing the system in action.

**Acceptance Criteria:**
- [ ] Create step-by-step demo guide
- [ ] Use example files from DEV-P2-28
- [ ] Show: Ingestion, Retrieval, Comparison, Inconsistency Detection
- [ ] Include expected outputs for each step
- [ ] Document common user questions and answers
- [ ] Save as `RAG_data/docs/DEMO_WALKTHROUGH.md`

**Dependencies:** DEV-P2-28

**Owner:** Tester

---

#### **TEST-P2-19: Manual Testing – Edge Cases**

**Priority:** P2

**Description:**
Test and document handling of edge cases and unusual scenarios.

**Acceptance Criteria:**
- [ ] Test with very large files (>100MB)
- [ ] Test with files containing special characters
- [ ] Test with files in various encodings
- [ ] Test with password-protected files (should fail gracefully)
- [ ] Test with nested directory structures
- [ ] Document results and system behavior
- [ ] Save as `RAG_data/docs/EDGE_CASES.md`

**Dependencies:** Phase 1 and Phase 2 complete

**Owner:** Tester

---

### 👀 Reviewer Tickets (Phase 4)

#### **REV-P2-11: Documentation Review**

**Priority:** P2

**Description:**
Review all documentation for completeness, accuracy, and usefulness.

**Acceptance Criteria:**
- [ ] Review README.md for clarity and completeness
- [ ] Review DEVELOPMENT.md for accuracy
- [ ] Review DEMO_WALKTHROUGH.md for usefulness
- [ ] Review EDGE_CASES.md for completeness
- [ ] Verify all documentation is up-to-date with implementation
- [ ] Approve or request improvements

**Dependencies:** DEV-P2-24, DEV-P2-25, DEV-P2-26, TEST-P2-18, TEST-P2-19

**Owner:** Reviewer

---

#### **REV-P2-12: Final Sign-off**

**Priority:** P2

**Description:**
Perform final review and approve the entire Independent RAG System for production use.

**Acceptance Criteria:**
- [ ] All P0 tickets are completed and approved
- [ ] All P1 tickets are completed and approved
- [ ] All P2 tickets are completed and approved
- [ ] All tests pass (≥80% coverage)
- [ ] All acceptance criteria are met
- [ ] System is production-ready
- [ ] Documentation is complete
- [ ] **Official approval** for system deployment

**Dependencies:** All other tickets (P0, P1, P2)

**Owner:** Reviewer

---

## 📋 Ticket Summary

### By Phase and Priority

| Phase | P0 | P1 | P2 | Total |
|-------|----|----|----|-------|
| **Developer** | 10 | 7 | 5 | 22 |
| **Tester** | 6 | 6 | 2 | 14 |
| **Reviewer** | 4 | 3 | 2 | 9 |
| **Total** | **20** | **16** | **9** | **45** |

### By Role

| Role | Count | Effort Estimate |
|------|-------|-----------------|
| Developer | 22 | ~11-13 days |
| Tester | 14 | ~8-9 days |
| Reviewer | 9 | ~3-4 days |
| **Total** | **45** | **~22-26 days** |

---

## 🎯 Next Stage

**Awaiting human validation** of these implementation tickets before proceeding to **Stage 7 – Implementation Loop** (actual code development against these tickets).

---
**Status**: Draft awaiting explicit human approval
