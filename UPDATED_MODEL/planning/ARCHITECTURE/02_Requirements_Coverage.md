# 02_Requirements_Coverage — Proposal → Implementation Mapping

Maps `01_Proposal.md` requirements to implementation decisions.

| Proposal Item | Implementation |
|---------------|----------------|
| Temporal validity #1 priority | Bi-temporal props on every node/edge; `current` flag; `valid_at` from extract.py |
| Reuse/improve `extract.py` | Wrapped as `temporal.timestamp_extractor` — reuse mtime; improve for audio/video mod dates |
| Conflict detection via entity identity + provenance | Graphiti episode identity + provenance metadata |
| Most-recent-wins + flag outdated | Auto-supersession edges (`SUPERSEDES`), `valid_at` comparison |
| All 3 modes prefer current=true | Retrieval filters on `current=true` by default |
| Historical only on explicit request | `as_of` and `include_history` params |
| Incremental update on `samples5/` | IntakeWatcher + Graphiti incremental episodes |
| Provenance: source file, extraction path, model | Stored per fact; surfaced in citations |

## OpenSpec Stage Alignment

| OpenSpec Stage | Artifact Location |
|---------------|-------------------|
| Proposal | `01_Proposal.md` (user-owned) |
| Analyst | `artifacts/specs.md` (existing) |
| Specifications | This architecture's `02_Requirements_Coverage.md` |
| Architect | `UPDATED_MODEL/ARCHITECTURE/01_Technical_Design.md` |
| Design | `UPDATED_MODEL/ARCHITECTURE/04_Database_Design.md` |
| Planner | `UPDATED_MODEL/ARCHITECTURE/03_Coding_Implementation_Plan.md` |
| Tasks | `UPDATED_MODEL/ARCHITECTURE/03_Coding...` Phase 1–6 |
| Tech Lead | (human) |
| Developer/Tester/Reviewer | Implementation team |

## Success Criteria (Evaluation Band)
See `10_Test_Plan.md` — temporal correctness tests, latency, Hit@K.

## Scope Boundaries (Inherited)
- In-scope: temporal modelling, conflict detection, 3 retrieval modes, incremental update
- Out-of-scope: UI, deployment automation, custom model training
