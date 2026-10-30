# ARCHITECTURE — README & Index

This directory contains the **technical design, planning artifacts, and implementation
plan** for the **Temporal-Valid Knowledge Graph RAG System**, assembled from the
`UPDATED_MODEL/` research and tailored specifically for a **military document
intelligence environment**.

Military constraints assumed throughout:
- Air-gapped / offline capability is mandatory (no cloud-only dependencies at runtime)
- All decisions favor low-latency, auditable, deterministic pipelines
- Data is **classified**; provenance, timestamps, and audit trails are load-bearing
- Documents share similar formats (field manuals, after-action reports, IFF/SOP,
  readiness reports, equipment logs, comms transcripts)
- External APIs (OpenAI) are only acceptable **behind an internal gateway**
  with redaction gate; nothing leaves the enclave

---

## Read Order (Architect → Implementer)

1. `01_Technical_Design.md` — System architecture, data flow, interfaces, deps
2. `02_Requirements_Coverage.md` — Mapping back to proposal/specs/test bands
3. `03_Coding_Implementation_Plan.md` — Phased plan + tasks + acceptance
4. `04_Database_Design.md` — Neo4j + Qdrant schema, indexes, query patterns
5. `05_Directory_Structure.md` — Final repo layout & file naming
6. `06_API_Contracts.md` — Interfaces (ingest, query, retrieval modes)
7. `07_Milestones.md` — Milestone plan with exit criteria
8. `08_Decisions_Log.md` — Answered analyst + OpenSpec questions, military rationale
9. `09_Risk_Failure_Modes.md` — Failure, security, perf, integration risks
10. `10_Test_Plan.md` — Unit, integration, temporal correctness, eval bands
11. `11_Handoff_Checklist.md` — Tech lead kickoff + DoD + sign-offs

---

## Document Status

- Status: **Ready for tech lead** (all design artifacts delivered)
- Scope: Full system implementation plan
- Deliverable: Working repository that ingests `samples5/` and answers in 3 retrieval modes
- Sign-offs required: Tech lead (design accept), Security officer (open security items), Mission lead (classification redaction scope)
