# 05_Directory_Structure — Final Repo Layout

```
mini-extract/
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── README.md
├── extract.py                        # Legacy entry point → kept as shim
├── main.py                           # New service entry (FastAPI)
├── src/
│   ├── config/                       # ConfigManager (pydantic Settings)
│   ├── intake/
│   │   ├── watcher.py                # watchdog file watcher
│   │   ├── queue.py                  # SQLite job queue
│   │   └── router.py                 # MIME/ext → handler
│   ├── extraction/
│   │   ├── dispatcher.py             # runs all paths
│   │   ├── text.py                   # docling text
│   │   ├── tables.py                 # docling tables
│   │   ├── vlm.py                    # conditional VLM
│   │   ├── audio.py                  # whisper via docling
│   │   ├── video.py                  # frame + audio
│   │   ├── ocr.py                    # tesseract fallback
│   │   └── archives.py               # zip/tar extract
│   ├── temporal/
│   │   ├── timestamp_extractor.py    # reused + improved extract.py
│   │   ├── temporal_kg.py            # Graphiti + Neo4j wrapper
│   │   └── kg_schema.py              # schema definitions
│   ├── reconstruction/
│   │   ├── entity_resolver.py        # Semantica merge
│   │   └── conflict_resolver.py      # supersession logic
│   ├── indexing/
│   │   └── hierarchical.py          # HiRAG communities
│   ├── retrieval/
│   │   ├── pure_rag.py
│   │   ├── rag_kg_validator.py
│   │   ├── kg_only.py
│   │   └── hybrid.py                 # orchestration
│   ├── generation/
│   │   ├── answer_gen.py             # DSPy
│   │   └── citations.py
│   ├── audit/
│   │   └── logger.py                 # append-only audit
│   ├── api/
│   │   └── server.py                 # FastAPI app
│   └── models/                       # pydantic models
├── tests/                              # provided temporal test suite + new
├── samples5/                           # watched drop folder
├── data/                               # dbms, qdrant, audit
├── artifacts/                          # proposals/specs (kept)
├── UPDATED_MODEL/
│   └── ARCHITECTURE/                 # this plan
└── README.md
```

## Naming Conventions
- Functions: `snake_case`, single-line docstrings.
- Class: `PascalCase`.
- All IO via pydantic models (`src/models/*`).
- No globals; use DI container (FastAPI Depends).
- Timestamps: UTC ISO-8601 with `Z` suffix.
- IDs: UUID4 strings.
