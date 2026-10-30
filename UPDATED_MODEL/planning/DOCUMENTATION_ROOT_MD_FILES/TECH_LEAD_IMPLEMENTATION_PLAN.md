---
format: html
---

# 🚀 TECH LEAD IMPLEMENTATION PLAN - Working UI with Proper Outputs

## Executive Summary

**Objective:** Implement the Temporal-Valid KG-RAG System to achieve a working UI that accepts queries and returns answers with proper citations, timestamps, and provenance.

**Current State:**
- ✅ Temporal core implemented (timestamp extraction, KG schema, conflict resolution)
- ✅ Retrieval modules implemented (Pure RAG, RAG+KG, KG-only)
- ✅ API server skeleton exists
- ❌ **Data ingestion pipeline incomplete**
- ❌ **Databases not integrated**
- ❌ **Generation module missing**
- ❌ **UI not connected to API**

**Target State:** Working system where users can:
1. Drop files into `samples5/` directory
2. Open UI in browser
3. Enter natural language queries
4. Receive answers with:
   - Fact content
   - Source file and page/location
   - Extraction path and model used
   - As-of timestamp
   - Confidence score
   - Supersession information

**Timeline:** 2-3 weeks (5 sprints @ 2 days each)

---

## 📋 TECH LEAD RESPONSIBILITIES

As Tech Lead, you are responsible for:

### Coordination
- [ ] Assign developers to specific modules (D1-D9)
- [ ] Ensure dependencies are respected (no one starts D2 before D1 is done)
- [ ] Hold daily standups during active development
- [ ] Track progress against this plan

### Quality Assurance
- [ ] Code review for all PRs
- [ ] Verify each milestone's exit criteria
- [ ] Run acceptance tests before merging
- [ ] Ensure temporal correctness (non-negotiable)

### Infrastructure
- [ ] Ensure Neo4j and Qdrant are available
- [ ] Validate all system dependencies
- [ ] Set up CI/CD for testing
- [ ] Configure environments (dev, staging, demo)

### Delivery
- [ ] Ensure UI meets usability standards
- [ ] Verify all three retrieval modes work
- [ ] Validate temporal correctness
- [ ] Conduct demo walkthrough

---

## 🎯 IMPLEMENTATION ROADMAP

### Phase Structure

Each phase has:
- **Duration:** 2 days
- **Objective:** Clear deliverable
- **Entry Criteria:** What must be true to start
- **Exit Criteria:** What must be true to finish
- **Success Metrics:** How we measure completion
- **Owner:**Who is responsible
- **Resources:** Reference materials

---

## 📅 PHASE 1: FOUNDATION & INTAKE (Days 1-2)

**Objective:** Set up infrastructure and implement file intake so documents can enter the system.

### Entry Criteria
- [x] Temporal core modules exist and work independently
- [x] Retrieval modules exist
- [x] Sample files available in SAMPLES/
- [ ] Developers assigned to Phase 1 tasks

### Work Breakdown

#### Task 1.1: Environment Setup (Day 1 Morning - All Hands)
**Owner:** Tech Lead + Developers  
**Effort:** 1-2 hours  

**Actions:**
1. Install system dependencies:
   ```bash
   # Ubuntu
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr tesseract-ocr-eng ffmpeg libgl1 poppler-utils
   
   # macOS
   brew install tesseract ffmpeg python-magic
   ```

2. Set up Python environment:
   ```bash
   cd /home/karthikean.juttumaha/mini-extract
   uv init
   uv add graphiti-core ragbrain docling docling-graph qdrant-client neo4j \
         dspy sentence-transformers python-dotenv watchdog python-magic fastapi uvicorn
   uv add -D pytest ruff
   uv sync
   ```

3. Start databases:
   ```bash
   # Neo4j (Docker)
   docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
     -v $(pwd)/data/neo4j:/data \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:5
   
   # Qdrant (Docker)
   docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
     -v $(pwd)/data/qdrant:/qdrant/storage \
     qdrant/qdrant
   ```

4. Create `.env` file:
   ```bash
   cp .env.example .env
   # Edit with actual values
   cat >> .env << EOF
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password
   QDRANT_URL=http://localhost:6333
   OPENAI_API_KEY=your-key-here
   OPENAI_BASE_URL=http://llm-gateway.internal/v1
   MODEL=gpt-4-turbo
   VLM_MODEL=gpt-4o
   EOF
   ```

**Exit Criteria:**
- [ ] `uv run python -c "import graphiti_core; import qdrant_client; import neo4j; print('All dependencies OK')"` succeeds
- [ ] `curl http://localhost:6333` returns Qdrant status
- [ ] Neo4j browser at `http://localhost:7474` is accessible

---

#### Task 1.2: Implement Intake Module (Day 1 Afternoon - Developer A)
**Owner:** Developer A  
**Effort:** 2-4 hours  
**Priority:** CRITICAL (blocks all other development)

**Files to Create:**
```
src/intake/
├── __init__.py
├── watcher.py      # File system watcher
├── queue.py        # SQLite job queue
└── router.py       # Format router
```

**Dependencies:**
- `watchdog` - File system monitoring
- `sqlite3` - Built-in, no install needed
- `python-magic` - MIME type detection

**Implementation Guide:**
See `UPDATED_MODEL/ARCHITECTURE/01_Technical_Design.md` Section 2  
See `UPDATED_MODEL/CODE DIRECTIONS AND PRODUCTS/04_CODE_SCAFFOLDS.md` - Intake templates

**Minimum Required Code:**

`src/intake/watcher.py`:
```python
import watchdog.events
import watchdog.observers
from pathlib import Path
from .queue import JobQueue

class FileEventHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, queue: JobQueue):
        self.queue = queue
        self.samples_dir = Path("samples5")
        self.samples_dir.mkdir(exist_ok=True)
    
    def on_created(self, event):
        if not event.is_directory and Path(event.src_path).parent == self.samples_dir:
            file_path = Path(event.src_path).relative_to(self.samples_dir)
            self.queue.enqueue(str(file_path))
            print(f"📥 File detected: {file_path} - enqueued for processing")
    
    def on_modified(self, event):
        if not event.is_directory and Path(event.src_path).parent == self.samples_dir:
            file_path = Path(event.src_path).relative_to(self.samples_dir)
            self.queue.enqueue(str(file_path))
            print(f"🔄 File modified: {file_path} - re-enqueued")

class IntakeWatcher:
    def __init__(self):
        self.queue = JobQueue()
        self.handler = FileEventHandler(self.queue)
        self.observer = None
    
    def start(self):
        self.observer = watchdog.observers.Observer()
        self.observer.schedule(self.handler, path=str(self.samples_dir), recursive=False)
        self.observer.start()
        print(f"👀 Watching {self.samples_dir} for new files...")
    
    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
```

`src/intake/queue.py`:
```python
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional
import uuid

class JobQueue:
    DEF DB_PATH = Path("data/job_queue.db")
    
    def __init__(self):
        self.db_path = self.DB_PATH
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    status TEXT DEFAULT 'queued',
                    created_at TEXT NOT NULL,
                    updated_at TEXT DEFAULT NULL,
                    processed_at TEXT DEFAULT NULL,
                    error TEXT DEFAULT NULL,
                    UNIQUE(file_path)
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_status ON jobs(status)')
            conn.commit()
    
    def enqueue(self, file_path: str) -> str:
        """Add file to queue. Returns job ID."""
        job_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT OR IGNORE INTO jobs (id, file_path, status, created_at) VALUES (?, ?, ?, ?)',
                (job_id, file_path, 'queued', now)
            )
            # Update existing job if needed
            conn.execute(
                'UPDATE jobs SET status = ? WHERE file_path = ? AND status != ?',
                ('queued', file_path, 'completed')
            )
            conn.commit()
        
        return job_id
    
    def dequeue(self) -> Optional[dict]:
        """Get next queued job. Returns job dict or None."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT id, file_path, created_at FROM jobs WHERE status = ? ORDER BY created_at ASC LIMIT 1',
                ('queued',)
            )
            job = cursor.fetchone()
            
            if job:
                job_id, file_path, created_at = job
                conn.execute(
                    'UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?',
                    ('processing', datetime.utcnow().isoformat() + "Z", job_id)
                )
                conn.commit()
                return {
                    'id': job_id,
                    'file_path': file_path,
                    'created_at': created_at
                }
        
        return None
    
    def mark_completed(self, job_id: str):
        """Mark job as completed."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'UPDATE jobs SET status = ?, processed_at = ? WHERE id = ?',
                ('completed', datetime.utcnow().isoformat() + "Z", job_id)
            )
            conn.commit()
    
    def mark_failed(self, job_id: str, error: str):
        """Mark job as failed."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'UPDATE jobs SET status = ?, error = ?, updated_at = ? WHERE id = ?',
                ('failed', error, datetime.utcnow().isoformat() + "Z", job_id)
            )
            conn.commit()
    
    def get_all(self):
        """Get all jobs."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM jobs ORDER BY created_at DESC')
            return [dict(zip(['id', 'file_path', 'status', 'created_at', 'updated_at', 
                            'processed_at', 'error'], row)) for row in cursor.fetchall()]
```

`src/intake/router.py`:
```python
import magic
from pathlib import Path
from typing import Literal

IngestMethod = Literal["text", "ocr", "audio", "video", "vlm", "table", "archive"]

class FormatRouter:
    """Route files to appropriate extraction path based on MIME type."""
    
    MIME_TO_METHOD: dict[str, IngestMethod] = {
        # Text
        'text/plain': 'text',
        'text/markdown': 'text',
        'application/json': 'text',
        'application/xml': 'text',
        
        # PDF
        'application/pdf': 'text',  # Will use OCR fallback if needed
        
        # Office
        'application/msword': 'text',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'text',
        'application/vnd.ms-excel': 'table',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'table',
        'application/vnd.ms-powerpoint': 'text',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'text',
        
        # Audio
        'audio/wav': 'audio',
        'audio/mpeg': 'audio',
        'audio/ogg': 'audio',
        'audio/m4a': 'audio',
        'audio/flac': 'audio',
        
        # Video
        'video/mp4': 'video',
        'video/webm': 'video',
        'video/quicktime': 'video',
        'video/x-matroska': 'video',
        
        # Images
        'image/png': 'vlm',
        'image/jpeg': 'vlm',
        'image/gif': 'vlm',
        'image/webp': 'vlm',
        
        # Archives
        'application/zip': 'archive',
        'application/x-tar': 'archive',
        'application/x-gzip': 'archive',
        'application/x-bzip2': 'archive',
    }
    
    @classmethod
    def get_method(cls, file_path: str) -> IngestMethod:
        """Get ingestion method for a file."""
        path = Path(file_path)
        
        # Try MIME type first
        try:
            mime = magic.from_file(str(path), mime=True)
            if mime in cls.MIME_TO_METHOD:
                return cls.MIME_TO_METHOD[mime]
        except Exception:
            pass
        
        # Fallback to extension
        ext = path.suffix.lower()
        ext_map: dict[str, IngestMethod] = {
            '.txt': 'text',
            '.md': 'text',
            '.json': 'text',
            '.xml': 'text',
            '.csv': 'table',
            '.pdf': 'text',  # Will use OCR if needed
            '.doc': 'text',
            '.docx': 'text',
            '.xls': 'table',
            '.xlsx': 'table',
            '.ppt': 'text',
            '.pptx': 'text',
            '.wav': 'audio',
            '.mp3': 'audio',
            '.m4a': 'audio',
            '.ogg': 'audio',
            '.mp4': 'video',
            '.mov': 'video',
            '.webm': 'video',
            '.png': 'vlm',
            '.jpg': 'vlm',
            '.jpeg': 'vlm',
            '.gif': 'vlm',
            '.zip': 'archive',
            '.tar': 'archive',
            '.gz': 'archive',
        }
        
        return ext_map.get(ext, 'text')
```

**Exit Criteria:**
- [ ] `src/intake/watcher.py` exists and is importable
- [ ] `src/intake/queue.py` exists and is importable
- [ ] `src/intake/router.py` exists and is importable
- [ ] Test passes:
  ```bash
  python -c "
  from src.intake.watcher import IntakeWatcher
  from src.intake.queue import JobQueue
  from src.intake.router import FormatRouter
  
  # Test queue
  q = JobQueue()
  job_id = q.enqueue('test.pdf')
  job = q.dequeue()
  assert job is not None
  assert job['file_path'] == 'test.pdf'
  q.mark_completed(job['id'])
  
  # Test router
  method = FormatRouter.get_method('test.pdf')
  assert method == 'text'
  
  print('✅ Intake module tests passed')
  "
  ```

---

## 📅 PHASE 2: EXTRACTION & RECONSTRUCTION (Days 3-4)

**Objective:** Parse documents and create facts in the Knowledge Graph with temporal attributes.

### Entry Criteria
- [ ] Phase 1 exit criteria met
- [ ] Intake module working
- [ ] Databases running

### Work Breakdown

#### Task 2.1: Implement Extraction Module (Day 3 - Developer B)
**Owner:** Developer B  
**Effort:** 4-6 hours  
**Dependencies:** D1 (Intake)

**Files to Create:**
```
src/extraction/
├── __init__.py
├── dispatcher.py     # Orchestrator
├── text.py           # Text extraction
├── tables.py         # Table extraction
├── vlm.py            # VLM enrichment
├── audio.py          # Audio transcription
├── video.py          # Video processing
├── ocr.py            # OCR fallback
└── archives.py       # Archive extraction
```

**Key Implementation:**

`src/extraction/dispatcher.py`:
```python
from pathlib import Path
from typing import Optional
from datetime import datetime
from .text import TextExtractor
from .tables import TableExtractor
from .vlm import VLMExtractor
from .ocr import OCRExtractor
from .audio import AudioExtractor
from .video import VideoExtractor
from .archives import ArchiveExtractor
from src.temporal.timestamp_extractor import get_file_timestamps
from src.intake.router import FormatRouter
from src.models import NormalizedExtract, Entity, Relation
import uuid

class ExtractionDispatcher:
    """Orchestrate multi-path extraction."""
    
    def __init__(self):
        self.extractors = {
            'text': TextExtractor(),
            'table': TableExtractor(),
            'ocr': OCRExtractor(),
            'audio': AudioExtractor(),
            'video': VideoExtractor(),
            'vlm': VLMExtractor(),
        }
        self.archive_extractor = ArchiveExtractor()
    
    def extract(self, file_path: str, samples_dir: Path = None) -> Optional[NormalizedExtract]:
        """Extract content from a file."""
        absolute_path = samples_dir / file_path if samples_dir else Path(file_path)
        
        if not absolute_path.exists():
            print(f"⚠️ File not found: {absolute_path}")
            return None
        
        # Get timestamps
        timestamps = get_file_timestamps(str(absolute_path))
        valid_at = timestamps.get('modified') or datetime.utcnow()
        
        # Get ingestion method
        ingest_method = FormatRouter.get_method(str(absolute_path))
        
        # Handle archives
        if ingest_method == 'archive':
            return self._extract_archive(absolute_path, valid_at, ingest_method)
        
        # Get extractor
        extractor = self.extractors.get(ingest_method)
        if not extractor:
            print(f"⚠️ No extractor for method: {ingest_method}")
            return None
        
        # Extract
        try:
            text = extractor.extract(absolute_path)
            entities = extractor.extract_entities(text)
            relations = extractor.extract_relations(text)
            metadata = {
                'file_size': absolute_path.stat().st_size,
                'file_type': ingest_method,
                'extraction_model': extractor.get_model(),
            }
            
            return NormalizedExtract(
                doc_id=str(uuid.uuid5(uuid.NAMESPACE_URL, str(absolute_path))),
                source_path=str(file_path),
                valid_at=valid_at,
                ingest_method=ingest_method,
                text=text,
                entities=entities,
                relations=relations,
                metadata=metadata
            )
        except Exception as e:
            print(f"❌ Extraction failed for {file_path}: {e}")
            return None
    
    def _extract_archive(self, archive_path: Path, valid_at: datetime, ingest_method: str):
        """Extract archive contents recursively."""
        # Implement archive extraction with depth limit <= 3
        pass
```

**Following the DRY principle, I'll reuse existing extraction logic where possible.**


**I see the existing** I'll focus on the core integration points that connect the system, avoiding redundant implementation details. The key is ensuring smooth information flow between modules, with clear interfaces for passing data and maintaining temporal consistency.

**I'll draft a concise implementation strategy** that bridges the existing components and highlights critical connection points for the Tech Lead.
