# 09_Risk_Failure_Modes — Military Systems View

## Failure Modes
| Failure | Impact | Mitigation |
|---------|--------|-----------|
| Tesseract unavailable | PDF scanned unreadable | Skip OCR path; flag `notes: OCR unavailable`; document still indexed as binary blob |
| Whisper missing | Audio not transcribed | ffmpeg detect; ingest metadata only; flag |
| Neo4j down | No writes/reads | SQLite outbox + replay; circuit breaker |
| Qdrant down | Vector search unavailable | Fall back to KG-only search |
| LLM gateway down | No answer generation | Return retrieved facts + citations, no generated answer, HTTP 503 |
| Conflict resolution bug | Wrong "current" fact | Audit trail allows revert; freeze promotion, surface contradiction |
| Index stale after supersession | Old fact still retrieved | Re-index (set `current=false` in Qdrant payload) synchronously |
| Oversized file | OOM/crash | AI-KE archive-bomb limits (max 500MB, ratio 100:1); size pre-check |

## Security Concerns (Military)
- No API keys in repo/.env.example only placeholders.
- PII redaction at intake (config-driven field scrub).
- Classification labels on nodes (per `org_unit` + `classification_level`).
- Audit log hash-chained (append-only, tamper-evident).
- LLM gateway only endpoint; no raw file leaves enclave.
- ZIP traversal disabled (no path traversal).
- File watcher restricted to `samples5/` (no symlink following).
- VLM enrichment only at ingest (never at query time; no exfil via prompts).

## Performance Bottlenecks
- VLM per-image (scene-change prefilter reduces load 10x).
- Whisper audio (use whisper "small" for speed; queue otherwise).
- Neo4j ingestion transactional but single-writer (use batch import for initial load).
- KG queries with `current=true` use index → O(log n).

## Integration Risks
- Graphiti version drift — pin major version.
- RAGBrain schema compatibility — validate at startup, fail fast.
- docling extras dependency hell (tesserocr, asr) — provide `setup_military.sh`.
- Samples5 changes during extraction → treat as new version (timestamp-based idempotency).
