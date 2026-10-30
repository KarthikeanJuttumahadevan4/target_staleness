---
format: html
---

# UPDATED_MODEL — System Overview

## Purpose

This directory contains the **planning and assembly artifacts** for the upgraded
**Temporal-Valid Knowledge Graph RAG System with Multi-Path Extraction**, as defined
in `01_Proposal.md`.

The goal is to take a **very basic RAG model** and, by **combining existing,
production-grade open-source Git projects**, evolve it into an advanced system that
supports:

- **Flexible document intake** (PDF, Excel, Word, audio, video, archives, images)
- **VLM enrichment** (charts, diagrams, tables, OCR)
- **Temporal reconstruction** (bi-temporal KG, supersession, provenance)
- **Hierarchical indexing** (layered KGs)
- **Hybrid retrieval** (Pure RAG / RAG+KG / KG-only, all temporal-aware)

> **No core algorithm is rewritten.** Existing projects are wired together through
> configuration and thin adapter code (~200 lines max).

---

## The Assembly Philosophy

```
Don't rebuild. Assemble. Wire. Configure. Ship.
```

Every subsystem in this plan is mapped to a **specific Git project** or library
that already implements it in production. The engineering effort is in:

1. **Integrating** via APIs
2. **Configuring** for the `samples5/` directory
3. **Adapting** output schemas
4. **Testing** the combined pipeline

---

## Document Index

| File | Purpose |
|------|---------|
| `01_Architecture.md` | Full assembled pipeline architecture |
| `02_Intake_Extraction.md` | Document intake and multi-path extraction |
| `03_VLM_Enrichment.md` | VLM-based visual content enrichment |
| `04_Reconstruction.md` | Temporal KG construction and conflict resolution |
| `05_Retrieval.md` | Hybrid retrieval (3 modes, temporal-aware) |
| `06_Model_Inventory.md` | Git projects used, developers, licenses |
| `07_Extraction_Methods_and_Papers.md` | Extraction techniques and supporting papers |

---

## Non-Functional Targets (Inherited from Proposal)

| Metric | Target |
|--------|--------|
| Document format coverage | ≥15 types (incl. audio, video, ZIP) |
| Temporal query accuracy | 100% most-recent-wins on conflict |
| Retrieval latency | <3s for 1K facts |
| Extraction accuracy | ≥85% F1 on tables/charts |
| Audit trail completeness | 100% (every fact traceable) |
| Incremental update | No full rebuild required |

---

## Status

- Draft awaiting human approval
- All downstream artifacts reference this overview
