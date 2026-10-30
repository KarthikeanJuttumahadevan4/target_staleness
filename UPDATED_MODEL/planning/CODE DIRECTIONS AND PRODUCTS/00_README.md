---
format: html
---

# CODE DIRECTIONS AND PRODUCTS — Coder Implementation Kit

## Purpose

This directory contains **coder-facing implementation directives** for the
Temporal-Valid Knowledge Graph RAG System. Because the environment restricts
creation of `.py` files directly, all Python code is delivered as **fenced
code blocks inside markdown**, ready to copy into the repo per the directory
layout in `ARCHITECTURE/05_Directory_Structure.md`.

> **Tech lead / coders:** copy each scaffold directly into the corresponding
> `.py` file. All interfaces, pydantic models, signatures, and behaviors are
> specified here. Fill in the `# TODO` markers and run tests listed in
> `05_ACCEPTANCE_CHECKS.md`.

## Directory index (read order)

1. `00_README.md` — this file; readiness gate
2. `01_READINESS_REPORT.md` — verified checklist of architecture docs
3. `02_MODULE_SPECS.md` — per-module function signatures + contracts
4. `03_INTERFACES_MODELS.md` — pydantic/dataclass models (copy-paste)
5. `04_CODE_SCAFFOLDS.md` — full Python scaffolds per file
6. `05_IMPLEMENTATION_ORDER.md` — dependency-ordered tasks
7. `06_DEPENDENCY_GRAPH.md` — import graph + risk matrix
8. `07_ACCEPTANCE_CHECKS.md` — per-module test recipes
9. `08_DEVELOPER_TASKS.md` — todowrite-style task list

## OpenSpec alignment
- Stage: **Planner → Tasks → Tech Lead → Developer**.
- This kit **is** the coding/implementation plan + technical directions.
- No `.py` is authored directly; all logic is conveyed here for developers to
  create `.py` files (per current repo permission constraints).
