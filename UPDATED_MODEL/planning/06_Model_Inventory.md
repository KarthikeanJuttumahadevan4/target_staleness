---
format: html
---

# 06_Model_Inventory — Git Projects Used & Developers

## Purpose

This document lists every Git project/library that will be **assembled** into
the new `UPDATED_MODEL` system, along with developer, license, and role.

---

## 📦 INTAKE & EXTRACTION (Stage 1)

### 1. AI-Knowledge-Engineer
- **Repo:** https://pypi.org/project/AI-Knowledge-Engineer/
- **Developer:** Knowledge-Engineer community
- **License:** MIT
- **Role:** Broadest intake (15+ formats incl. audio/video); 9-stage pipeline; ZIP bomb protection
- **Used in:** Intake Step 1 (DISCOVER, CLASSIFY, EXTRACT)

### 2. Docling
- **Repo:** https://github.com/DS4SD/docling
- **Developer:** IBM Research (Docling team)
- **License:** MIT
- **Role:** Layout-preserving PDF/text extraction; table structure recognition
- **Used in:** Intake Step 2 (PARSE for PDFs, Office)

### 3. Docs2KG
- **Repo:** https://github.com/yrules/Docs2KG
- **Developer:** yrules (research group)
- **License:** Apache 2.0 / MIT (check)
- **Role:** Dual-path processing (text + visual); unified multimodal KG
- **Used in:** Intake Step 3 (EXTRACT: text + layout + tables + figures)

### 4. Semantica
- **Repo:** https://github.com/semantica-agi/semantica
- **Developer:** Semantica AI
- **License:** MIT
- **Role:** FileIngestor; NER; RelationExtractor; GraphBuilder; merge_entities
- **Used in:** Entity/relation extraction; entity deduplication

### 5. Scinr / newton
- **Repo:** https://github.com/Scinr-AI/scinr
- **Developer:** Scinr AI
- **License:** Apache 2.0
- **Role:** 5-stage LLM pipeline; idempotent Neo4j writes; tabular bypass
- **Used in:** Alternative extraction path for structured docs

---

## 🎨 VLM ENRICHMENT (Stage 2)

### 6. Docling-Graph
- **Repo:** https://github.com/docling-project/docling-graph
- **Developer:** Docling Team (IBM Research)
- **License:** MIT
- **Role:** Schema-driven extraction; VLM + LLM backends; deterministic grounding
- **Models:** Any LiteLLM provider (Ollama, vLLM, OpenAI, Gemini, Mistral, IBM watsonx)
- **Used in:** Primary VLM enrichment layer

### 7. Diagram2Graph
- **Repo:** https://dev.to/sujiths/diagram2graph-fine-tuning-a-vision-language-model-to-extract-knowledge-graphs-from-diagrams-5f7p
- **Developer:** Sujith S (community)
- **License:** Apache 2.0 (model + code)
- **Model:** Qwen2.5-VL-3B (fine-tuned via PEFT/LoRA)
- **Role:** Diagram/flowchart → KG JSON
- **Benchmarks:** Node F1 89.1%, Edge F1 69.45%
- **Used in:** Specialized diagram extraction

### 8. Multi-VIE / Qwen2.5-VL-7B-SFT
- **Repo:** https://github.com/FairmeHIT/Multi-VIE
- **Developer:** Huafu Li, Guo Chen, et al. (Harbin Institute of Technology)
- **License:** Code MIT; Model on HuggingFace
- **Model:** Qwen2.5-VL-7B-SFT (fine-tuned)
- **Role:** Forms, certificates, invoices, tabular forms
- **Benchmarks:** 93.65% F1, 0.93 NED (multi-type VIE)
- **Used in:** Specialized form/certificate extraction

### 9. VaLiK
- **Repo:** https://github.com/Wings-Of-Disaster/VaLiK
- **Developer:** Junming Liu, Siyuan Meng, et al. (ICCV 2025)
- **License:** MIT
- **Role:** Annotation-free multimodal KG construction; Chain-of-Experts VLM
- **Used in:** Image-only documents, MMKG construction

### 10. VisRAG
- **Repo:** https://github.com/openbmb/visrag
- **Developer:** OpenBMB / Tsinghua University
- **License:** Apache 2.0
- **Role:** Direct image embedding (no OCR); VLM retrieval
- **Benchmarks:** 20-40% improvement vs text RAG
- **Used in:** Fallback VLM retrieval when text extraction fails

### 11. Multi-modal VDU / VISR-KGC
- **Repos:** Research papers (see 07)
- **Role:** Reference for advanced VLM + graph fusion methods

---

## 🔄 TEMPORAL KG CONSTRUCTION (Stage 3)

### 12. Graphiti
- **Repo:** https://github.com/getzep/graphiti
- **Developer:** Zep Inc.
- **License:** Apache 2.0
- **Stars:** 32K
- **Role:** Primary KG engine; bi-temporal facts; episodes; provenance; hybrid retrieval
- **Used in:** All stages (reconstruction + indexing + retrieval)

### 13. RAGBrain
- **Repo:** https://github.com/Nagendhra-Madishetti/ragbrain
- **Developer:** Nagendhra Madishetti
- **License:** Apache 2.0
- **Role:** Conflict resolution layer; bi-temporal (4 timestamps); supersession; checked generation
- **Used in:** Reconstruction (conflict resolution); Retrieval (checked answers)

### 14. zeit
- **Repo:** https://github.com/kborovik/zeit
- **Developer:** kborovik
- **License:** (zeit-graph on PyPI; check)
- **Role:** Lightweight bi-temporal; alternative temporal layer
- **Used in:** Fallback if Graphiti alone insufficient (audit)

### 15. context-graph
- **Repo:** https://github.com/williebsweet/context-graph
- **Developer:** williebsweet
- **License:** (check)
- **Role:** Conflict taxonomy (4 types); resolution strategies; CGR3 reasoning
- **Used in:** Reference for conflict detection classification

### 16. Silk
- **Repo:** https://github.com/Kieleth/silk-graph
- **Developer:** Kieleth
- **License:** MIT (PyPI + crate)
- **Role:** Merkle-CRDT conflict-free KG; ontology enforcement
- **Used in:** Optional distributed/sync scenarios only

### 17. Lighthouse Memory
- **Repo:** https://pypi.org/project/lighthouse-graph/
- **Developer:** Lighthouse KG team
- **License:** MIT
- **Role:** Versioned facts by rule; never overwrites; time travel
- **Used in:** Audit-only alternative (no overwrites guarantee)

### 18. Semantica (TemporalVersionManager)
- **Repo:** https://github.com/semantica-agi/semantica
- **Role:** KG versioning; SHA-256 snapshots; compliance (HIPAA, SOX, GDPR)
- **Used in:** Periodic snapshot + audit (optional)

### 19. KektorDB
- **Repo:** https://github.com/sanonone/kektordb
- **Developer:** sanonone
- **License:** Apache 2.0 (source-available)
- **Role:** Temporal decay; contradiction detection; self-managing memory
- **Used in:** Optional cognitive engine layer

### 20. TypedMemory
- **Repo:** https://pypi.org/project/typedmem/
- **License:** MIT
- **Role:** Contract-driven memory; explicit conflict policies
- **Used in:** Optional (if strict schema governance needed)

---

## 📊 HIERARCHICAL INDEXING (Stage 4)

### 21. HiRAG (research code)
- **Paper:** ACL 2025 (Findings of EMNLP)
- **Authors:** (see arxiv:2025.findings-emnlp.321)
- **Role:** 3-level hierarchical KG indexing
- **Use:** Reference implementation for layered context

### 22. HyGRAG
- **Repo:** https://github.com/zjunet/HyGRAG
- **Developer:** zjunet
- **License:** (check)
- **Role:** Hybrid graph (chunk + entity); dynamic updates without rebuild
- **Use case:** Hierarchical index maintenance

### 23. KG-Retriever (research)
- **Paper:** arxiv.org/html/2412.05547v1
- **Role:** Hierarchical Index Graph (HIG) approach
- **Use:** Reference for document/entity layers

### 24. Helix
- **Repo:** https://github.com/YashNuhash/Helix
- **Developer:** YashNuhash
- **License:** MIT
- **Role:** Fuses LightRAG + Graphiti; multi-hop + CFI verification
- **Use in:** Retrieval enhancement (Stage 5)

---

## 🔍 HYBRID RETRIEVAL (Stage 5)

### 25. Helix (Retrieval Use)
- **Repo:** [see above]
- **Roles:** BFS multi-hop; Composite Fidelity Index; temporal context
- **Used in:** Mode B (RAG+KG Validator) enhancement

### 26. Engram
- **Repo:** https://github.com/jamjet-labs/engram
- **Developer:** Jamjet Labs
- **License:** Apache 2.0 (check)
- **Role:** HybridRetriever (vector + keyword + temporal); Reader modes
- **Used in:** Mature retrieval + temporal scoring

### 27. HydraClaim
- **Repo:** https://pypi.org/project/hydraclaim/
- **Developer:** HydraDB team
- **License:** (check)
- **Role:** Graph-probe routing (FAST/DEEP/ABSTAIN); bitemporal reads
- **Used in:** Query routing optimization

### 28. CKS-MCP
- **Repo:** https://pypi.org/project/cks-mcp/
- **License:** MIT
- **Role:** Contradiction detection; version control; 3-way merge
- **Used in:** Optional audit/conflict analysis layer

---

## 🧩 SUPPORTING UTILITIES

### 29. ReasonGraph
- **Repo:** https://pypi.org/project/reasongraph/
- **Developer:** ReasonGraph community
- **License:** MIT
- **Role:** Agent memory; conflict resolution; time-travel; causal tracing
- **Used in:** Optional agent memory layer

### 30. Universal / Standard Libraries
| Library | Role |
|--------|------|
| `watchdog` | File watching `samples5/` |
| `python-magic` | MIME detection |
| `zipfile` | Archive extraction |
| `openpyxl`, `pandas` | XLSX/CSV parsing |
| `pydub`, `librosa`, `whisper` | Audio transcription |
| `opencv-python`, `moviepy` | Video frame extraction |
| `pytesseract` | OCR |
| `networkx` | In-memory graphs |

---

## 📜 LICENSE SUMMARY

| License | Projects |
|---------|----------|
| **Apache 2.0** | Graphiti, RAGBrain, Scinr, Helix, HydraClaim, CKS-MCP, KektorDB, Engram, Docling, Docs2KG, Diagram2Graph, AI-Knowledge-Engineer, Semantica, VisRAG |
| **MIT** | Docling-Graph, Multi-VIE, VaLiK, Silk, TypedMemory, ReasonGraph, Lighthouse, AI-KE, CKS |
| **Other/Proprietary** | zeit-graph (zeit), Helix (check), fgraph |

> ⚠️ Note: verify each project's LICENSE file at integration time; some
> use dual-licensing (e.g., Graphiti enterprise features beyond core).

---

## 👥 NOTABLE RESEARCH ORGANIZATIONS INVOLVED

| Org | Projects |
|-----|----------|
| **IBM Research** | Docling, Docling-Graph |
| **Zep Inc.** | Graphiti |
| **Tsinghua University / OpenBMB** | VisRAG |
| **Harbin Institute of Technology** | Multi-VIE / Qwen2.5-VL-7B-SFT |
| **ACL/CVPR/ICCV Authors** | VaLiK (ICCV 2025), HiRAG (EMNLP 2025), Diagram2Graph |
<|message|> **Community** | yrules (Docs2KG), Helix, context-graph, zeit |

---

## 📋 INTEGRATION DECISIONS AWAITING HUMAN VALIDATION

1. **Primary KG backend:** Neo4j (mature) vs FalkorDB (temporal-native, fast)?
2. **Primary VLM:** Qwen2.5-VL-7B-SFT (local) vs GPT-4o Vision (cloud)?
3. **Retrieval fusion:** RAGBrain alone vs Graphiti + RAGBrain stack?
4. **Entity resolution:** Semantica (ML) vs Graphiti built-in (LLM)?
5. **Snapshot frequency:** Per-ingest vs weekly? (Semantica TemporalVersionManager)
6. **Which projects are "core" vs "optional/fallback"?** (Recommend marking with tier)
