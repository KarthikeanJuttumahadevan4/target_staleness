# 03_RAG_Specifications.md – Independent RAG Technical Specifications

## 1. Overview

This document translates the **approved requirements** in `02_RAG_Requirements_Analysis.md` into precise technical specifications. It defines exact interfaces, data contracts, algorithms, and configuration for the Independent RAG System.

### 1.1 document structure
- **Section 2**: Component architecture and interfaces
- **Section 3**: Data models and type definitions
- **Section 4**: Algorithms (chunking, embedding, retrieval, deduction)
- **Section 5**: Vector store schema and payloads
- **Section 6**: Comparison and resolution algorithms
- **Section 7**: File and module layout
- **Section 8**: Acceptance criteria and test scenarios
- **Section 9**: Configuration parameters

### 1.2 dependeNCIES
| Component | Source | Version | Purpose |
|-----------|--------|---------|---------|
| Qdrant | Local | v1.8.0+ | Vector store for embeddings and payloads |
| sentence-transformers | Local | all-MiniLM-L6-v2 | Embedding model (primary) |
| BAAI/bge-small-en | Local | v1.5 | Embedding model (fallback) |
| pdfplumber | Local | latest | PDF text extraction |
| python-docx | Local | latest | DOCX text extraction |
| openpyxl | Local | latest | Excel data extraction |
| python-pptx | Local | latest | PPTX text extraction |
| pytesseract | Local | latest | OCR for scanned PDFs |
| extract.py | Local | existing | Timestamp extraction |

---

## 2. Component Specifications

### 2.1 Module Hierarchy
```
RAG_data/
├── src/
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── file_ingestor.py       # FR-ING-001, FR-ING-002, FR-ING-003, FR-ING-004
│   │   └── config.py
│   │
│   ├── chunking/
│   │   ├── __init__.py
│   │   ├── text_chunkers.py        # FR-CHK-001, FR-CHK-002, FR-CHK-003
│   │   └── table_chunkers.py       # FR-CHK-004
│   │
│   ├── embedding/
│   │   ├── __init__.py
│   │   ├── embedder.py             # FR-EMB-001, FR-EMB-002
│   │   └── models.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_searcher.py      # FR-RET-001, FR-RET-002, FR-RET-003
│   │   └── deducer.py              # FR-RET-004
│   │
│   ├── deduction/
│   │   ├── __init__.py
│   │   ├── fact_deducer.py         # FR-DED-001, FR-DED-002, FR-DED-003
│   │   └── normalizer.py
│   │
│   ├── comparison/
│   │   ├── __init__.py
│   │   ├── aligner.py              # FR-CMP-001, FR-CMP-002, FR-CMP-003, FR-CMP-004
│   │   └── detectors.py
│   │
│   ├── resolution/
│   │   ├── __init__.py
│   │   ├── resolver.py             # Section 5 rules
│   │   └── reports.py
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── qdrant_client.py
│   │   └── jsonl_store.py
│   │
│   └── config.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── data/
│
├── deductions.jsonl               # FR-DED-004
├── resolution_log.jsonl           # Section 5.4
└── config.yaml
```

---

### 2.2 Component Interfaces

#### **2.2.1 File Ingestor (`ingestion.file_ingestor.py`)**

**Class**: `FileIngestor`

```python
class FileIngestor:
    def __init__(self, 
                 base_path: str = "samples5",
                 watch: bool = False,
                 allowed_extensions: List[str] = [".txt", ".pdf", ".docx", ".xlsx", ".pptx"]):
        """
        Ingests files from base_path.
        
        Args:
            base_path: Directory to ingest from
            watch: If True, runs in watch mode (incremental)
            allowed_extensions: File extensions to process
        """
    
    def ingest_all(self) -> List[IngestionResult]:
        """
        Batch ingest all files in base_path.
        
        Returns:
            List of IngestionResult objects (one per file)
            
        Raises:
            FileNotFoundError: If base_path does not exist
            PermissionError: If files cannot be read
        """
    
    def ingest_one(self, file_path: str) -> IngestionResult:
        """
        Ingest a single file.
        
        Args:
            file_path: Absolute path to the file
            
        Returns:
            IngestionResult object
        """
    
    def start_watcher(self, callback: Callable[[str], None]) -> None:
        """
        Start file system watcher (if watch=True).
        
        Args:
            callback: Function(event_type: str, file_path: str) called on file changes
        """
    
    def stop_watcher(self) -> None:
        """Stop the file system watcher."""

class IngestionResult:
    file_path: str
    file_hash: str
    as_of: datetime
    timestamp_fallback: bool
    success: bool
    error: Optional[str]
    chunks: List[Chunk]
```

**Algorithms**: See Section 4.1

---

#### **2.2.2 Text Chunkers (`chunking.text_chunkers.py`)**

**Class**: `TextChunker`

```python
class TextChunker:
    def __init__(self,
                 chunk_size: int = 512,
                 overlap: int = 102,
                 min_chunk_size: int = 50):
        """
        Splits text into chunks with overlap.
        
        Args:
            chunk_size: Maximum tokens per chunk
            overlap: Number of overlapping tokens
            min_chunk_size: Minimum tokens per chunk (smaller chunks are merged)
        """
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Split plain text into chunks.
        
        Args:
            text: Raw text content
            metadata: File-level metadata to attach to each chunk
            
        Returns:
            List of Chunk objects
        """

class TableChunker:
    def __init__(self):
        """Splits table data into row-based chunks."""
    
    def chunk_table(self, 
                    data: List[List[str]], 
                    headers: List[str],
                    metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Split table rows into chunks.
        
        Args:
            data: 2D list of cell values
            headers: Column headers
            metadata: File-level metadata
            
        Returns:
            List of Chunk objects
        """

class Chunk:
    chunk_id: str
    content: str
    file_path: str
    file_hash: str
    as_of: datetime
    chunk_index: int
    total_chunks: int
    start_offset: int
    end_offset: int
    metadata: Dict[str, Any]
```

---

#### **2.2.3 Embedder (`embedding.embedder.py`)**

**Class**: `Embedder`

```python
class Embedder:
    def __init__(self,
                 model_name: str = "all-MiniLM-L6-v2",
                 batch_size: int = 32):
        """
        Generates embeddings for text using local models.
        
        Args:
            model_name: Name of the embedding model
            batch_size: Number of texts to embed in a single batch
        """
    
    def load_model(self) -> None:
        """
        Load the embedding model.
        
        Raises:
            ImportError: If required model package is not installed
            RuntimeError: If model cannot be loaded
        """
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each vector is List[float])
            
        Raises:
            ValueError: If texts list is empty
        """
    
    def embed_single(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector (List[float])
        """
```

---

#### **2.2.4 Vector Searcher (`retrieval.vector_searcher.py`)**

**Class**: `VectorSearcher`

```python
class VectorSearcher:
    def __init__(self, 
                 collection_name: str = "rag_deductions",
                 host: str = "localhost",
                 port: int = 6333):
        """
        Interacts with Qdrant vector store.
        
        Args:
            collection_name: Name of the Qdrant collection
            host: Qdrant server host
            port: Qdrant server port
        """
    
    def initialize_collection(self, 
                             vector_size: int = 384,
                             distance: str = "Cosine") -> None:
        """
        Create or reconfigure the Qdrant collection.
        
        Args:
            vector_size: Dimension of embedding vectors
            distance: Distance metric (Cosine, Dot, Euclidean)
        """
    
    def index(self, 
              vectors: List[List[float]],
              payloads: List[Dict[str, Any]],
              ids: Optional[List[str]] = None) -> None:
        """
        Index embeddings with payloads.
        
        Args:
            vectors: List of embedding vectors
            payloads: List of payload dictionaries (one per vector)
            ids: Optional list of IDs (generated if None)
        """
    
    def search(self,
               query_vector: List[float],
               limit: int = 10,
               filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """
        Search the vector index.
        
        Args:
            query_vector: Embedding of the query
            limit: Maximum number of results
            filters: Optional Qdrant filter expression
            
        Returns:
            List of SearchResult objects, sorted by similarity
        """
    
    def delete_by_file(self, file_path: str) -> None:
        """
        Delete all entries for a specific file.
        
        Args:
            file_path: Path of the file to delete
        """

class SearchResult:
    id: str
    score: float
    payload: Dict[str, Any]
    vector: Optional[List[float]]
```

---

#### **2.2.5 Fact Deducer (`deduction.fact_deducer.py`)**

**Class**: `FactDeducer`

```python
class FactDeducer:
    def __init__(self,
                 predicate_map: Optional[Dict[str, str]] = None,
                 confidence_threshold: float = 0.7):
        """
        Extracts structured facts from chunks.
        
        Args:
            predicate_map: Custom mapping of keywords to predicates
            confidence_threshold: Minimum confidence for a deduction
        """
    
    def deduct(self, chunk: Chunk) -> List[RAGDeduction]:
        """
        Extract facts from a chunk.
        
        Args:
            chunk: Chunk object to process
            
        Returns:
            List of RAGDeduction objects
        """
    
    def deduct_batch(self, chunks: List[Chunk]) -> List[RAGDeduction]:
        """
        Extract facts from multiple chunks.
        
        Args:
            chunks: List of Chunk objects
            
        Returns:
            List of RAGDeduction objects
        """
```

---

#### **2.2.6 Aligner (`comparison.aligner.py`)**

**Class**: `Aligner`

```python
class Aligner:
    def __init__(self,
                 similarity_threshold: float = 0.85,
                 confidence_threshold: float = 0.9):
        """
        Aligns RAG deductions with KG facts.
        
        Args:
            similarity_threshold: Minimum similarity for semantic matching
            confidence_threshold: Minimum confidence for fuzzy matching
        """
    
    def align(self,
              rag_deductions: List[RAGDeduction],
              kg_facts: List[KGFact]) -> List[Alignment]:
        """
        Find matches between RAG deductions and KG facts.
        
        Args:
            rag_deductions: List of RAG deduction objects
            kg_facts: List of KG fact objects (from Neo4j query)
            
        Returns:
            List of Alignment objects
        """

class Alignment:
    rag_deduction: RAGDeduction
    kg_fact: Optional[KGFact]  # None if no match
    alignment_type: str  # "exact", "fuzzy", "semantic", "none"
    confidence: float
```

---

#### **2.2.7 Inconsistency Detector (`comparison.detectors.py`)**

**Class**: `InconsistencyDetector`

```python
class InconsistencyDetector:
    def detect(self,
               alignments: List[Alignment]) -> List[Inconsistency]:
        """
        Detect inconsistencies from alignments.
        
        Args:
            alignments: List of Alignment objects
            
        Returns:
            List of Inconsistency objects
        """

class Inconsistency:
    inconsistency_id: str
    conflict_type: str  # "value_conflict", "rag_missing", "kg_missing", etc.
    severity: str  # "high", "medium", "low"
    rag_deduction: Optional[RAGDeduction]
    kg_fact: Optional[KGFact]
    details: Dict[str, Any]
```

---

#### **2.2.8 Resolver (`resolution.resolver.py`)**

**Class**: `Resolver`

```python
class Resolver:
    def __init__(self,
                 rules: Optional[Dict[str, ResolutionRule]] = None):
        """
        Resolves inconsistencies using rules or escalates to human.
        
        Args:
            rules: Dict of rule_id -> ResolutionRule
        """
    
    def resolve(self,
                inconsistency: Inconsistency) -> ResolutionResult:
        """
        Attempt to resolve an inconsistency.
        
        Args:
            inconsistency: Inconsistency to resolve
            
        Returns:
            ResolutionResult object
            
        Raises:
            HumanEscalationError: If no auto-resolution possible (signals need for human)
        """

class ResolutionRule:
    rule_id: str
    priority: int
    condition: Callable[[Inconsistency], bool]
    action: Callable[[Inconsistency], ResolutionAction]

class ResolutionResult:
    inconsistency_id: str
    rule_applied: Optional[str]
    action: ResolutionAction
    resolved: bool
    human_escalation: bool
    report: Optional[Dict[str, Any]]

class ResolutionAction:
    action_type: str  # "prefer_rag", "prefer_kg", "merge", "discard"
    target: str  # "rag" or "kg"
    details: Dict[str, Any]
```

---

#### **2.2.9 Reporter (`resolution.reports.py`)**

**Functions**:

```python
def generate_escalation_report(inconsistency: Inconsistency,
                               rag_deduction: RAGDeduction,
                               kg_fact: KGFact) -> Dict[str, Any]:
    """
    Generate a human-readable escalation report.
    
    Args:
        inconsistency: The inconsistency object
        rag_deduction: The RAG deduction involved
        kg_fact: The KG fact involved
        
    Returns:
        Dictionary containing the full report (can be serialized to markdown/JSON)
    """

def log_resolution(result: ResolutionResult) -> None:
    """
    Log a resolution to resolution_log.jsonl.
    
    Args:
        result: ResolutionResult to log
    """
```

---

## 3. Data Models and Type Definitions

### 3.1 RAG Deduction Schema (Python TypedDict)

```python
from typing import TypedDict, Optional, List, Any
from datetime import datetime

class Provenance(TypedDict):
    extraction_path: str
    model_used: str
    raw_text: str

class RAGDeduction(TypedDict, total=False):
    deduction_id: str
    source_file_path: str
    chunk_id: str
    as_of: str  # ISO 8601 datetime string
    subject_entity: str
    subject_entity_type: Optional[str]
    predicate: str
    object_value: str  # or could be Union[str, int, float, bool] but stored as string
    object_type: str  # "text", "numeric", "boolean", "date"
    extraction_method: str  # "regex", "keyword", "table", "llm"
    confidence: float
    provenance: Provenance
    metadata: Dict[str, Any]
```

### 3.2 KG Fact Schema (TypedDict)

```python
class KGFact(TypedDict, total=False):
    fact_id: str
    entity_id: str
    predicate: str
    object_value: str
    as_of: str  # ISO 8601 datetime string
    current: bool
    superseded_by: Optional[str]
    supersedes: Optional[List[str]]
    valid_from: Optional[str]
    valid_to: Optional[str]
    provenance_id: str
```

### 3.3 JSON Schemas (for validation)

See `RAG_data/schemas/` for full JSON Schema definitions for both RAG deduction and KG fact validation.

---

## 4. Algorithms

### 4.1 File Ingestion Algorithm

```
ALGORITHM: ingest_files(base_path: str, watch: bool)
INPUT:
    base_path: Directory containing source files
    watch: If True, run in watch mode
OUTPUT:
    List[IngestionResult] for batch mode, or None for watch mode

IF watch:
    Initialize file system watcher on base_path
    FOR each file change event:
        IF event is MODIFY or CREATE:
            result = ingest_single_file(event.src_path)
            IF callback provided:
                callback(event, result)
    RETURN None

ELSE:
    results = []
    FOR each file in base_path (recursive):
        IF file.extension in allowed_extensions:
            result = ingest_single_file(file)
            results.append(result)
    RETURN results

FUNCTION ingest_single_file(file_path: str) -> IngestionResult:
    TRY:
        file_hash = calculate_sha256(file_path)
        as_of, timestamp_fallback = TimestampExtractor().get_as_of(file_path)
        
        IF file previously ingested AND file_hash unchanged:
            RETURN IngestionResult(file_path, file_hash, as_of, timestamp_fallback, 
                                   success=True, chunks=[], error=None)
        
        raw_text = extract_text(file_path)  // Use file-type-specific extractors
        
        chunker = SELECT_CHUNKER(file_path)  // TextChunker or TableChunker
        chunks = chunker.chunk(raw_text, {
            "file_path": file_path,
            "file_hash": file_hash,
            "as_of": as_of
        })
        
        RETURN IngestionResult(file_path, file_hash, as_of, timestamp_fallback,
                               success=True, chunks=chunks, error=None)
    
    CATCH Exception as e:
        RETURN IngestionResult(file_path, file_hash, as_of, timestamp_fallback,
                               success=False, chunks=[], error=str(e))
```

---

### 4.2 Chunking Algorithm

```
ALGORITHM: chunk_text(text: str, chunk_size: int, overlap: int, metadata: dict) -> List[Chunk]
INPUT:
    text: Raw text content
    chunk_size: Maximum tokens per chunk
    overlap: Number of overlapping tokens
    metadata: File-level metadata
OUTPUT:
    List[Chunk]

tokens = TOKENIZE(text)
effective_chunk_size = chunk_size - overlap
chunks = []

FOR i FROM 0 TO len(tokens) STEP effective_chunk_size:
    start = i
    end = min(i + chunk_size, len(tokens))
    
    IF end - start < min_chunk_size AND i > 0:
        // Merge with previous chunk
        continue
    
    chunk_text = DETOKENIZE(tokens[start:end])
    
    chunk = Chunk(
        chunk_id = generate_id(metadata["file_path"], start),
        content = chunk_text,
        file_path = metadata["file_path"],
        file_hash = metadata["file_hash"],
        as_of = metadata["as_of"],
        chunk_index = len(chunks),
        start_offset = start,
        end_offset = end,
        metadata = metadata
    )
    chunks.append(chunk)

RETURN chunks
```

---

### 4.3 Table Chunking Algorithm

```
ALGORITHM: chunk_table(data: List[List[str]], headers: List[str], metadata: dict) -> List[Chunk]
INPUT:
    data: 2D list of cell values
    headers: Column headers
    metadata: File-level metadata
OUTPUT:
    List[Chunk]

chunks = []

FOR row_index, row in enumerate(data):
    // Create markdown table row
    content = "| " + " | ".join(row) + " |"
    
    chunk = Chunk(
        chunk_id = generate_id(metadata["file_path"], row_index),
        content = content,
        file_path = metadata["file_path"],
        file_hash = metadata["file_hash"],
        as_of = metadata["as_of"],
        chunk_index = row_index,
        start_offset = row_index,
        end_offset = row_index + 1,
        metadata = {
            **metadata,
            "table_headers": headers,
            "row_number": row_index,
            "extraction_path": "excel_table"
        }
    )
    chunks.append(chunk)

RETURN chunks
```

---

### 4.4 Embedding Algorithm

```
ALGORITHM: embed_texts(texts: List[str], model: Embedder) -> List[List[float]]
INPUT:
    texts: List of text strings
    model: Loaded embedding model
OUTPUT:
    List[List[float]] (embeddings)

IF model not loaded:
    model.load_model()

batches = SPLIT_INTO_BATCHES(texts, batch_size=32)
embeddings = []

FOR batch in batches:
    batch_embeddings = model.encode(batch, normalize_embeddings=True)
    embeddings.extend(batch_embeddings.tolist())

RETURN embeddings
```

---

### 4.5 Fact Deduction Algorithm

```
ALGORITHM: deduct_facts(chunk: Chunk) -> List[RAGDeduction]
INPUT:
    chunk: Chunk object with content and metadata
OUTPUT:
    List[RAGDeduction]

deductions = []

// Step 1: Extract entities and values using regex patterns
patterns = [
    (r"(?:price|cost|amount)[\s:]*[ $]?(\d+[.,]?\d*)", "has_price", "numeric"),
    (r"headcount[\s:]*(\d+)", "has_headcount", "numeric"),
    (r"budget[\s:]*[ $]?(\d+[.,]?\d*)", "has_budget", "numeric"),
    (r"(?:date|as of|effective)[\s:]+(\d{4}-\d{2}-\d{2})", "has_date", "date"),
    // Add more patterns as needed
]

FOR pattern, predicate, object_type in patterns:
    matches = REGEX_FINDALL(pattern, chunk.content, re.IGNORECASE)
    
    FOR match in matches:
        deduction = RAGDeduction(
            deduction_id = generate_deduction_id(chunk, predicate, match),
            source_file_path = chunk.file_path,
            chunk_id = chunk.chunk_id,
            as_of = chunk.as_of,
            subject_entity = extract_subject_entity(chunk.content, predicate),
            subject_entity_type = infer_entity_type(subject_entity),
            predicate = predicate,
            object_value = normalize_value(match, object_type),
            object_type = object_type,
            extraction_method = "regex",
            confidence = 0.95,  // Default for regex
            provenance = {
                "extraction_path": chunk.metadata.get("extraction_path", "text"),
                "model_used": "regex_patterns",
                "raw_text": chunk.content
            },
            metadata = chunk.metadata
        )
        deductions.append(deduction)

// Step 2: Table-based deduction (if chunk has table data)
IF "table_headers" in chunk.metadata:
    headers = chunk.metadata["table_headers"]
    row_data = parse_table_row(chunk.content)
    
    FOR col_index, value in enumerate(row_data):
        header = headers[col_index]
        predicate = map_header_to_predicate(header)
        
        IF predicate IS NOT None:
            deduction = RAGDeduction(
                deduction_id = generate_deduction_id(chunk, predicate, value),
                source_file_path = chunk.file_path,
                chunk_id = chunk.chunk_id,
                as_of = chunk.as_of,
                subject_entity = headers[0] if headers else "unknown",  // First col = entity
                predicate = predicate,
                object_value = normalize_value(value, infer_type(value)),
                object_type = infer_type(value),
                extraction_method = "table",
                confidence = 0.98,  // Higher confidence for tables
                provenance = {
                    "extraction_path": "excel_table",
                    "model_used": "table_parser",
                    "raw_text": chunk.content
                },
                metadata = chunk.metadata
            )
            deductions.append(deduction)

RETURN deductions

FUNCTION normalize_value(value: str, object_type: str) -> str:
    IF object_type == "numeric":
        value = EXTRACT_NUMBER(value)
    ELSE IF object_type == "date":
        value = PARSE_DATE(value).isoformat()
    ELSE:
        value = value.strip().lower()
    RETURN value
```

---

### 4.6 Retrieval Algorithm

```
ALGORITHM: retrieve(query: str, limit: int = 10) -> List[RAGDeduction]
INPUT:
    query: User query string
    limit: Maximum number of results
OUTPUT:
    List[RAGDeduction] sorted by relevance

// Step 1: Embed query
query_embedding = embedder.embed_single(query)

// Step 2: Vector search
search_results = vector_searcher.search(
    query_vector=query_embedding,
    limit=limit * 2,  // Retrieve extra for re-ranking
    filters=None
)

// Step 3: Re-rank by temporal recency
deductions = []
FOR result in search_results:
    payload = result.payload
    chunk = Chunk(**payload["chunk"])
    dests = load_deductions_for_chunk(chunk.chunk_id)
    
    FOR ded in dests:
        ded.score = result.score
        ded.as_of_dt = parse_iso(ded.as_of)
        deductions.append(ded)

// Step 4: Sort by composite score
SORT deductions BY:
    Primary: score (descending)
    Secondary: as_of_dt (descending)

RETURN deductions[:limit]
```

---

## 5. Vector Store Schema

### 5.1 Qdrant Collection Configuration

```json
{
  "collection_name": "rag_deductions",
  "vectors": {
    "size": 384,
    "distance": "Cosine"
  },
  "optimizers_config": {
    "default_segment_number": 1,
    "max_optimization_threads": 4
  },
  "wal_config": {
    "wal_capacity_mb": 1024,
    "wal_segments_ahead": 0
  }
}
```

### 5.2 Payload Schema

Each vector index entry **shall** have the following payload:

```json
{
  "chunk_id": "INV-2024-001_abc123_0",
  "file_path": "samples5/invoices/INV-2024-001.pdf",
  "file_hash": "sha256:abc123...",
  "as_of": "2024-09-01T10:00:00+00:00",
  "content": "Invoice INV-2024-001...",
  "chunk_index": 0,
  "total_chunks": 5,
  "start_offset": 0,
  "end_offset": 512,
  "extraction_path": "pdf_text",
  
  "deductions": [
    {
      "deduction_id": "ded_abc123",
      "subject_entity": "Product_X",
      "subject_entity_type": "product",
      "predicate": "has_price",
      "object_value": "100",
      "object_type": "numeric",
      "extraction_method": "regex",
      "confidence": 0.95
    }
  ],
  
  "metadata": {
    "page_number": 1,
    "table_headers": null,
    "row_number": null
  }
}
```

**Indexing Strategy**:
- Primary vector: Embedding of `content`
- Secondary index: `file_path` (for batch deletion)
- Secondary index: `as_of` (for temporal filtering)
- Secondary index: `subject_entity` (for entity-based queries)

---

## 6. Comparison and Resolution Algorithm

### 6.1 Alignment Algorithm

```
ALGORITHM: align_deductions(rag_deductions: List[RAGDeduction], 
                           kg_facts: List[KGFact]) -> List[Alignment]
INPUT:
    rag_deductions: List of RAG deductions
    kg_facts: List of KG facts (from Neo4j query)
OUTPUT:
    List[Alignment]

alignments = []

// Step 1: Exact matching by key
FOR rag in rag_deductions:
    key = (rag.subject_entity, rag.predicate, rag.source_file_path)
    
    Matches = FILTER kg_facts WHERE
        kg.entity_id == rag.subject_entity AND
        kg.predicate == rag.predicate AND
        (kg.provenance.source_file_path == rag.source_file_path OR
         kg.provenance.source_file_path IS NULL)
    
    IF Matches NOT EMPTY:
        best_kg = SELECT BEST from Matches:
            WHERE current == True
            ORDER BY as_of DESC
            LIMIT 1
        
        alignment = Alignment(
            rag_deduction = rag,
            kg_fact = best_kg,
            alignment_type = "exact",
            confidence = 1.0
        )
        alignments.append(alignment)

// Step 2: Fuzzy matching by entity + predicate
unmatched_rag = FILTER rag_deductions NOT IN alignments
unmatched_kg = FILTER kg_facts NOT IN alignments

FOR rag in unmatched_rag:
    Matches = FILTER kg_facts WHERE
        kg.entity_id == rag.subject_entity AND
        kg.predicate == rag.predicate
    
    IF Matches NOT EMPTY:
        best_kg = SELECT BEST from Matches:
            WHERE current == True
            ORDER BY as_of DESC
            LIMIT 1
        
        // Calculate confidence based on value similarity
        confidence = calculate_value_similarity(rag.object_value, best_kg.object_value)
        
        IF confidence >= 0.9:
            alignment = Alignment(
                rag_deduction = rag,
                kg_fact = best_kg,
                alignment_type = "fuzzy",
                confidence = confidence
            )
            alignments.append(alignment)

// Step 3: Semantic matching using embeddings
still_unmatched_rag = FILTER rag_deductions NOT IN alignments
still_unmatched_kg = FILTER kg_facts NOT IN alignments

IF still_unmatched_rag NOT EMPTY AND still_unmatched_kg NOT EMPTY:
    // Create embeddings for all unmatched items
    rag_embeddings = embedder.embed([rag.subject_entity + " " + rag.predicate + " " + rag.object_value 
                                    FOR rag IN still_unmatched_rag])
    kg_embeddings = embedder.embed([kg.entity_id + " " + kg.predicate + " " + kg.object_value 
                                   FOR kg IN still_unmatched_kg])
    
    // Calculate similarity matrix
    FOR i, rag IN enumerate(still_unmatched_rag):
        FOR j, kg IN enumerate(still_unmatched_kg):
            sim = cosine_similarity(rag_embeddings[i], kg_embeddings[j])
            
            IF sim >= 0.85:
                alignment = Alignment(
                    rag_deduction = rag,
                    kg_fact = kg,
                    alignment_type = "semantic",
                    confidence = sim
                )
                alignments.append(alignment)

// Step 4: Mark unmatched items
FOR rag IN rag_deductions:
    IF rag NOT IN alignments:
        alignment = Alignment(
            rag_deduction = rag,
            kg_fact = None,
            alignment_type = "none",
            confidence = 0.0
        )
        alignments.append(alignment)

RETURN alignments

FUNCTION calculate_value_similarity(val1: str, val2: str) -> float:
    // Normalize both values
    n1 = normalize_value(val1, infer_type(val1))
    n2 = normalize_value(val2, infer_type(val2))
    
    IF n1 == n2:
        RETURN 1.0
    
    // Try numeric comparison
    TRY:
        num1 = float(n1)
        num2 = float(n2)
        RETURN 1.0 - (abs(num1 - num2) / max(abs(num1), abs(num2), 1.0))
    EXCEPT:
        PASS
    
    // Fallback to string similarity
    RETURN string_similarity(n1, n2)
```

---

### 6.2 Inconsistency Detection Algorithm

```
ALGORITHM: detect_inconsistencies(alignments: List[Alignment]) -> List[Inconsistency]
INPUT:
    alignments: List of Alignment objects
OUTPUT:
    List[Inconsistency]

inconsistencies = []

FOR alignment IN alignments:
    rag = alignment.rag_deduction
    kg = alignment.kg_fact
    
    IF alignment.alignment_type == "none":
        IF kg IS NOT None:
            // RAG has no matching deduction for a KG fact
            inconsistency = Inconsistency(
                inconsistency_id = generate_id(),
                conflict_type = "rag_missing",
                severity = "medium",
                rag_deduction = None,
                kg_fact = kg,
                details = {
                    "missing_entity": rag.subject_entity,
                    "missing_predicate": rag.predicate
                }
            )
            inconsistencies.append(inconsistency)
        ELSE:
            // KG has no matching fact for a RAG deduction
            inconsistency = Inconsistency(
                inconsistency_id = generate_id(),
                conflict_type = "kg_missing",
                severity = "medium",
                rag_deduction = rag,
                kg_fact = None,
                details = {}
            )
            inconsistencies.append(inconsistency)
    
    ELSE:
        // Both exist - check for conflicts
        rag_val = normalize_value(rag.object_value, rag.object_type)
        kg_val = normalize_value(kg.object_value, "text")  // KG stores as string
        
        IF rag_val != kg_val:
            inconsistency = Inconsistency(
                inconsistency_id = generate_id(),
                conflict_type = "value_conflict",
                severity = "high",
                rag_deduction = rag,
                kg_fact = kg,
                details = {
                    "rag_value": rag_val,
                    "kg_value": kg_val,
                    "rag_as_of": rag.as_of,
                    "kg_as_of": kg.as_of
                }
            )
            inconsistencies.append(inconsistency)
        
        ELSE IF rag.as_of != kg.as_of:
            inconsistency = Inconsistency(
                inconsistency_id = generate_id(),
                conflict_type = "temporal_conflict",
                severity = "medium",
                rag_deduction = rag,
                kg_fact = kg,
                details = {
                    "rag_as_of": rag.as_of,
                    "kg_as_of": kg.as_of
                }
            )
            inconsistencies.append(inconsistency)

RETURN inconsistencies
```

---

### 6.3 Resolution Algorithm

```
ALGORITHM: resolve_inconsistency(inconsistency: Inconsistency) -> ResolutionResult
INPUT:
    inconsistency: Inconsistency to resolve
OUTPUT:
    ResolutionResult

// Define resolution rules in priority order
rules = [
    ResolutionRule(
        rule_id="R1",
        priority=0,
        condition=lambda ic: ic.conflict_type == "exact_match",
        action=lambda ic: ResolutionAction(
            action_type="no_action",
            target=None,
            details={"status": "consistent"}
        )
    ),
    ResolutionRule(
        rule_id="R2",
        priority=1,
        condition=lambda ic: (
            ic.conflict_type == "value_conflict" OR 
            ic.conflict_type == "temporal_conflict"
        ) AND (
            parse_iso(ic.details.get("rag_as_of", "")) > 
            parse_iso(ic.details.get("kg_as_of", ""))
        ),
        action=lambda ic: ResolutionAction(
            action_type="prefer_rag",
            target="rag",
            details={"reason": "Temporal validity - RAG is newer"}
        )
    ),
    ResolutionRule(
        rule_id="R3",
        priority=1,
        condition=lambda ic: (
            ic.conflict_type == "value_conflict" OR 
            ic.conflict_type == "temporal_conflict"
        ) AND (
            parse_iso(ic.details.get("kg_as_of", "")) > 
            parse_iso(ic.details.get("rag_as_of", ""))
        ),
        action=lambda ic: ResolutionAction(
            action_type="prefer_kg",
            target="kg",
            details={"reason": "Temporal validity - KG is newer"}
        )
    ),
    ResolutionRule(
        rule_id="R4",
        priority=2,
        condition=lambda ic: (
            ic.conflict_type == "value_conflict" AND
            ic.rag_deduction.metadata.get("extraction_path") == "excel_table"
        ),
        action=lambda ic: ResolutionAction(
            action_type="prefer_rag",
            target="rag",
            details={"reason": "Structured table data > text inference"}
        )
    ),
    ResolutionRule(
        rule_id="R5",
        priority=2,
        condition=lambda ic: (
            ic.conflict_type == "value_conflict" AND
            len(ic.kg_fact.get("supersedes", [])) > 0
        ),
        action=lambda ic: ResolutionAction(
            action_type="prefer_kg",
            target="kg",
            details={"reason": "KG has explicit provenance chain"}
        )
    ),
    ResolutionRule(
        rule_id="R6",
        priority=3,
        condition=lambda ic: (
            ic.conflict_type == "value_conflict" AND
            is_numeric(ic.rag_deduction.object_value) AND
            not is_numeric(ic.kg_fact.object_value)
        ),
        action=lambda ic: ResolutionAction(
            action_type="prefer_rag",
            target="rag",
            details={"reason": "RAG value is numeric, KG is text"}
        )
    ),
    ResolutionRule(
        rule_id="R7",
        priority=3,
        condition=lambda ic: (
            ic.conflict_type == "value_conflict" AND
            is_iso_date(ic.rag_deduction.object_value) AND
            not is_iso_date(ic.kg_fact.object_value)
        ),
        action=lambda ic: ResolutionAction(
            action_type="prefer_rag",
            target="rag",
            details={"reason": "RAG date is ISO format, KG is natural text"}
        )
    )
]

// Sort rules by priority (lower = higher priority)
SORT rules BY priority ASCENDING

FOR rule IN rules:
    IF rule.condition(inconsistency):
        action = rule.action(inconsistency)
        
        RETURN ResolutionResult(
            inconsistency_id = inconsistency.inconsistency_id,
            rule_applied = rule.rule_id,
            action = action,
            resolved = True,
            human_escalation = False,
            report = None
        )

// No rule matched - escalate to human
report = generate_escalation_report(inconsistency)
RAISE HumanEscalationError(report)

// Note: HumanEscalationError should be caught by the caller and trigger report generation
```

---

## 7. File and Module Layout

```
RAG_data/
├── README.md
├── 01_RAG_Proposal.md              # Stage 1
├── 02_RAG_Requirements_Analysis.md # Stage 2
├── 03_RAG_Specifications.md        # Stage 3 (this file)
│
├── schemas/
│   ├── rag_deduction_schema.json
│   └── kg_fact_schema.json
│
├── src/
│   ├── __init__.py
│   │
│   ├── config.py                  # Global configuration
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── file_ingestor.py
│   │   └── watcher.py
│   │
│   ├── chunking/
│   │   ├── __init__.py
│   │   ├── text_chunkers.py
│   │   ├── table_chunkers.py
│   │   └── utils.py
│   │
│   ├── embedding/
│   │   ├── __init__.py
│   │   ├── embedder.py
│   │   └── models.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_searcher.py
│   │   └── retriever.py
│   │
│   ├── deduction/
│   │   ├── __init__.py
│   │   ├── fact_deducer.py
│   │   ├── normalizer.py
│   │   └── patterns.py
│   │
│   ├── comparison/
│   │   ├── __init__.py
│   │   ├── aligner.py
│   │   ├── detectors.py
│   │   └── comparators.py
│   │
│   ├── resolution/
│   │   ├── __init__.py
│   │   ├── resolver.py
│   │   ├── reports.py
│   │   └── actions.py
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── qdrant_client.py
│   │   └── jsonl_store.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       ├── tokens.py
│       └── helpers.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_ingestor.py
│   │   ├── test_chunkers.py
│   │   ├── test_embedder.py
│   │   ├── test_retriever.py
│   │   ├── test_deducer.py
│   │   ├── test_aligner.py
│   │   ├── test_detectors.py
│   │   └── test_resolver.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_full_pipeline.py
│   │   ├── test_comparison.py
│   │   └── test_resolution.py
│   │
│   └── data/
│       ├── sample_files/
│       └── expected_outputs/
│
├── deductions.jsonl               # Persistent RAG deductions
├── resolution_log.jsonl           # Resolution history
├── config.yaml                    # Configuration
└── requirements.txt               # Python dependencies
```

---

## 8. Acceptance Criteria and Test Scenarios

### 8.1 Acceptance Criteria

| ID | Criteria | Test Method |
|----|----------|-------------|
| **AC-001** | System ingests all files in samples5/ without accessing Neo4j | Integration test: `test_full_pipeline.py::test_ingest_without_kg` |
| **AC-002** | All files are chunked and indexed with metadata | Unit test: `test_ingestor.py::test_chunking_complete` |
| **AC-003** | Embeddings are generated for all chunks | Unit test: `test_embedder.py::test_embedding_generation` |
| **AC-004** | RAG can retrieve relevant chunks for queries | Integration test: `test_retriever.py::test_retrieval_relevance` |
| **AC-005** | Fact deductions are extracted from chunks | Unit test: `test_deducer.py::test_fact_extraction` |
| **AC-006** | RAG deductions align with KG facts at ≥90% rate | Integration test: `test_comparison.py::test_alignment_rate` |
| **AC-007** | Inconsistencies are detected for intentionally conflicting data | Integration test: `test_comparison.py::test_inconsistency_detection` |
| **AC-008** | ≥80% of inconsistencies are auto-resolved | Integration test: `test_resolution.py::test_auto_resolution_rate` |
| **AC-009** | Human escalation reports are generated for unresolved inconsistencies | Unit test: `test_resolver.py::test_human_escalation` |
| **AC-010** | System handles malformed files without crashing | Unit test: `test_ingestor.py::test_error_handling` |
| **AC-011** | Performance meets targets (ingestion, indexing, query) | Integration test: `test_full_pipeline.py::test_performance` |

### 8.2 Test Scenarios

#### **Scenario 1: Basic Ingestion and Retrieval**
1. Place test files in `samples5/`
2. Run ingestion pipeline
3. Query for "price"
4. Verify results contain price-related deductions

#### **Scenario 2: Inconsistency Detection**
1. Create two versions of a file with conflicting price values
2. Run both KG and RAG pipelines
3. Run comparison
4. Verify inconsistency is detected
5. Verify auto-resolution selects the newer version

#### **Scenario 3: Human Escalation**
1. Create a file with ambiguous interpretation
2. Run both pipelines
3. Verify human escalation report is generated
4. Verify report contains both sides and recommendations

#### **Scenario 4: Temporal Supersession**
1. Create file v1 with price=100 (timestamp T1)
2. Create file v2 with price=120 (timestamp T2 > T1)
3. Run ingestion
4. Verify RAG returns price=120 as current
5. Verify KG also returns price=120
6. Verify comparison shows consistency

#### **Scenario 5: Missing Data**
1. Remove a file from RAG ingestion
2. Run comparison
3. Verify "RAG missing" inconsistency is detected
4. Verify report identifies the missing fact

---

## 9. Configuration Parameters

All parameters **shall** be configurable via `RAG_data/config.yaml` and environment variables.

### 9.1 Configuration File (`config.yaml`)

```yaml
# File Ingestion
ingestion:
  base_path: "samples5"
  watch_mode: false
  allowed_extensions:
    - ".txt"
    - ".pdf"
    - ".docx"
    - ".xlsx"
    - ".pptx"
  batch_size: 100

# Chunking
chunking:
  chunk_size: 512
  overlap: 102
  min_chunk_size: 50

# Embedding
embedding:
  model_name: "all-MiniLM-L6-v2"
  fallback_model: "BAAI/bge-small-en-v1.5"
  batch_size: 32
  normalize: true

# Vector Store
vector_store:
  host: "localhost"
  port: 6333
  collection_name: "rag_deductions"
  vector_size: 384
  distance: "Cosine"

# Fact Deduction
deduction:
  confidence_threshold: 0.7
  predicate_map:
    price: "has_price"
    cost: "has_price"
    amount: "has_price"
    headcount: "has_headcount"
    employees: "has_headcount"
    budget: "has_budget"
    date: "has_date"
    "as of": "has_date"
    effective: "has_date"

# Comparison
comparison:
  similarity_threshold: 0.85
  confidence_threshold: 0.9

# Resolution
resolution:
  rules:
    - R1
    - R2
    - R3
    - R4
    - R5
    - R6
    - R7

# Directories
directories:
  output: "RAG_data/output"
  logs: "RAG_data/logs"
  deductions_file: "RAG_data/deductions.jsonl"
  resolution_log: "RAG_data/resolution_log.jsonl"

# Performance
performance:
  max_file_size_mb: 100
  max_concurrent_files: 10
  query_timeout_ms: 500
```

### 9.2 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RAG_BASE_PATH` | Override base_path | `samples5` |
| `RAG_WATCH_MODE` | Enable watch mode | `false` |
| `RAG_MODEL` | Embedding model | `all-MiniLM-L6-v2` |
| `RAG_VECTOR_HOST` | Vector store host | `localhost` |
| `RAG_VECTOR_PORT` | Vector store port | `6333` |
| `RAG_CHUNK_SIZE` | Chunk size in tokens | `512` |
| `RAG_OVERLAP` | Overlap in tokens | `102` |
| `RAG_CONFIDENCE_THRESHOLD` | Min confidence | `0.7` |

---

## 10. Next Stage

**Awaiting human validation** of this specification before proceeding to **Stage 4 – Architect / Design** (`04_RAG_Architecture.md`).

---
**Status**: Draft awaiting explicit human approval
