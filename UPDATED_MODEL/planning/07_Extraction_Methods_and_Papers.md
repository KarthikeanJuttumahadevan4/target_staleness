# 07_Extraction_Methods_and_Papers

## Purpose

Document the **extraction methods** used in the assembled system and the
**academic papers** that support each method. All methods are **referenced,
not reimplemented** — sourced from existing open-source projects.

---

## A. Extraction Method Taxonomy

### A.1 — Text Extraction (Library-Based)

| Method | Description | Libraries | Papers |
|--------|-------------|-----------|--------|
| **Native PDF parsing** | Extract text from PDF content streams without OCR | PyMuPDF, PDFMiner, pdfplumber | [Bansal 2025 — PDF Ingestion for LLMs in RAG](https://doi.org/10.12732/ijam.v38i3s.163) |
| **DOCX/PPTX parsing** | Parse Office Open XML format | python-docx, python-pptx | [Docs2KG (Sun et al., 2025)](https://doi.org/10.1145/3701716.3715309) |
| **HTML parsing** | Extract text from HTML DOM | BeautifulSoup, lxml | Standard |
| **XLSX parsing** | Read cell values, formulas, tables | openpyxl, pandas | Standard |
| **Audio transcription** | Speech → text via Whisper | OpenAI Whisper, faster-whisper | [OpenAI Whisper paper](https://arxiv.org/abs/2212.04356) |
| **Video processing** | Frame extraction + OCR + metadata | OpenCV, moviepy | Various |

---

### A.2 — OCR (Optical Character Recognition)

| Method | Description | Libraries | Papers |
|--------|-------------|-----------|--------|
| **Tesseract (LSTM)** | Neural OCR engine, 100+ languages | Tesseract 5.x, pytesseract | [Smith 2007 — Tesseract](https://doi.org/10.1109/ICDAR.2007.4376991) |
| **EasyOCR** | CRNN-based OCR, Python-native | EasyOCR | [EasyOCR GitHub](https://github.com/JaidedAI/EasyOCR) |
| **PaddleOCR** | End-to-end OCR with layout analysis | PaddleOCR | [PaddlePaddle](https://github.com/PaddlePaddle/PaddleOCR) |
| **DocTR** | PyTorch/TensorFlow OCR | docTR | [Mindee docTR](https://github.com/mindee/doctr) |

**Supporting survey:**
> **PDF Information Extraction Survey** — Atagong et al. (2025), *"A review on knowledge and information extraction from PDF documents"*.
> Focus: Preprocessing → OCR → extraction → KG storage.
> Link: https://doi.org/10.3389/frai.2025.1466092

---

### A.3 — Layout Analysis (Visual Structure)

| Method | Description | Libraries | Papers |
|--------|-------------|-----------|--------|
| **CNN Layout Detection** | Detect regions (text, table, figure) | DocLayout-YOLO, LayoutLMv3 | [LayoutLMv3 (Huang et al., 2022)](https://arxiv.org/abs/2204.08387) |
| **Reading Order Estimation** | Reconstruct text flow | LayoutXLM | [LayoutXLM (Xu et al., 2021)](https://arxiv.org/abs/2104.08836) |
| **Rule-Based Layout** | Heuristic region segmentation | PDFminer, custom | [Binmakhashen & Mahmoud 2019 — Survey](https://doi.org/10.1109/ACCESS.2019.2908548) |

**Supporting survey:**
> **Document Understanding Survey** — Xu et al. (2020), *"A Survey on Document Understanding"*.
> Link: https://arxiv.org/abs/2011.13534 (hf-mirror copy)

---

### A.4 — Table Extraction

| Method | Description | Libraries | Papers |
|--------|-------------|-----------|--------|
| **Table Detection (CNN)** | Detect table boundaries | YOLO-based, TableSense | [TableSense (Dong et al., 2019)](https://doi.org/10.1145/3292500.3330969) |
| **Table Structure Recognition** | Row/column/cell extraction | Docling, TableFormer | [TableFormer (Nassar et al., 2022)](https://arxiv.org/abs/2203.01017) |
| **Cell Cell Analysis (TUTA)** | Pre-train LM for cell understanding | TUTA | [TUTA (Wang et al., 2020)](https://doi.org/10.1145/3394486.3403233) |
| **Multi-page table merge** | Continuity header detection + stitch | AI-KE, Marker, MinerU | — |

**Supporting tutorials/papers:**
> **Table Extraction & Understanding Tutorial** — Burdick et al. (VLDB 2020), *"Table Extraction and Understanding for Scientific and Enterprise Applications"*.
> Link: https://vldb.org/pvldb/vol13/p3433-burdick.pdf

> **PDF Ingestion for LLMs in RAG** — Bansal (2025).
> Specifically discusses table complexity: multi-level headers, merged cells, multi-page tables.
> Link: https://doi.org/10.12732/ijam.v38i3s.163

---

### A.5 — VLM Extraction (Vision-Language Models)

| Method | Description | Libraries | Papers |
|--------|-------------|-----------|--------|
| **Visual Document Understanding (VRDU)** | VLMs on document images | Qwen2.5-VL, LayoutLM, GPT-4o | [Liu et al. 2025 — "Deep Learning based Visually Rich Document Content Understanding: A Survey"](https://arxiv.org/html/2408.01287v2) |
| **Direct image embedding (VisRAG)** | Embed document pages directly, no OCR | VisRAG-Ret | [Tang et al., 2025 — VisRAG](https://arxiv.org/html/2410.10594) |
| **Diagram → KG (fine-tuned VLM)** | Qwen2.5-VL-3B fine-tuned on diagrams | Diagram2Graph | [Sujith S — Diagram2Graph (DEV.to)](https://dev.to/sujiths/diagram2graph-...) |
| **Form/certificate extraction** | Classification-guided LVLM | Multi-VIE (Qwen2.5-VL-7B-SFT) | [Li et al., 2026 — "Visual information extraction from documents via classification-guided LVLM"](https://doi.org/10.1016/j.engappai.2024.109040) |
| **Multimodal KG construction** | Chain-of-Experts VLM, no annotation | VaLiK | [Liu et al., ICCV 2025 — "Aligning Vision to Language: Annotation-Free MMKG Construction"](https://openaccess.thecvf.com/content/ICCV2025/papers/Liu_Aligning_Vision_to_Language_Annotation-Free_Multimodal_Knowledge_Graph_Construction_for_ICCV_2025_paper.pdf) |

---

### A.6 — Visual Extraction (Image → Facts)

| Method | Description | Papers |
|--------|-------------|--------|
| **Hierarchical KG from Images** | VLM extract attributes + LLM inferring + hierarchy expansion | [E-commerce Product KG (arxiv 2410.21237)](https://arxiv.org/html/2410.21237) |
| **VLM as KG extractor** | VLM generates text descriptions → NER → facts | Docs2KG, Docling-Graph |

---

## B. Supporting Papers (By Topic)

### B.1 — Document-to-KG Construction

1. **Docs2KG (Sun et al., 2025)** — *"Docs2KG: A Human-LLM Collaborative Approach to Unified Knowledge Graph Construction from Heterogeneous Documents"*.
   - ACM Digital Library: https://doi.org/10.1145/3701716.3715309
   - Provides unified Layout + Metadata + Semantic KG
   - Human-in-the-loop verification interface
   - Modular, supports 4 Semantic KG construction paradigms

2. **Knowledge Graph Construction: Extraction, Learning, and Application (Choi & Jung, 2025)**.
   - MDPI: https://www.mdpi.com/2076-3417/15/7/3727
   - Surveys extraction techniques (rule-based, ML, LLM-based)
   - Covers pipelines, storage, ontology

3. **Unstructured to Structured: Building KGs from Documents for Web Applications (Sun et al., 2026)**.
   - ACM: https://doi.org/10.1145/3774905.3793920
   - Multi-dimensional extraction: entities, relations, events, temporal, spatial, visual, metadata

4. **Scholarly PDF → KG (Giannopoulou, 2026)**.
   - URL: https://pyxida.aueb.gr/items/f6c75ceb-...
   - End-to-end: parsing → extraction → schema-based → RDF → KG
   - Compares parsers (textual + reading order metrics)

---

### B.2 — Document Layout & Structure Understanding

5. **Survey: Reading Order, Table of Contents, and Structure Extraction (Giovannini & Marinai, ICCV 2025)**.
   - PDF: https://openaccess.thecvf.com/...
   - Covers LayoutLM, reading order estimation, structure extraction
   - 50+ methods reviewed

6. **"Deep Learning based Visually Rich Document Content Understanding: A Survey" (arxiv 2408.01287)**.
   - https://arxiv.org/html/2408.01287v2
   - Comprehensive VRDU survey (OCR-based + OCR-free)
   - Compares LayoutLM, Donut, VLM approaches

---

### B.3 — Table Extraction

7. **"Table Extraction and Understanding for Scientific and Enterprise Applications" — Burdick et al., VLDB 2020**.
   - https://vldb.org/pvldb/vol13/p3433-burdick.pdf
   - 4 categories: Analysis, Detection, Refinement, Learning
   - Covers header hierarchy, multi-page tables, cell semantic linking

8. **"PDF Ingestion for LLMs in RAG Architectures" — Bansal (2025)**.
   - https://doi.org/10.12732/ijam.v38i3s.163
   - Pipeline vs end-to-end vs hybrid vs graph-based approaches
   - Detailed table extraction challenges section

---

### B.4 — VLM + Knowledge Graph Integration

9. **"Aligning Vision to Language: Annotation-Free MMKG Construction" — VaLiK (Liu et al., ICCV 2025)**.
   - https://openaccess.thecvf.com/content/ICCV2025/papers/Liu_Aligning_Vision_to_Language...
   - Chain-of-Experts VLM pipeline
   - Cross-modal similarity verification for noise filtering
   - Storage-efficient MMKG construction

10. **"Diagram2Graph: Fine-Tuning VLM for Diagram-to-KG" — Sujith S (2025, DEV.to)**.
    - https://dev.to/sujiths/diagram2graph-...
    - Qwen2.5-VL-3B fine-tuned with LoRA
    - Node F1 +14.2%, Edge F1 +23.4%

11. **"Visual information extraction from documents via classification-guided LVLM" — Li et al. (2026)**.
    - https://doi.org/10.1016/j.engappai.2024.109040
    - Qwen2.5-VL-7B-SFT model
    - Classification-guided prompt engineering
    - Benchmark: 93.65% F1 on 16 certificate types

12. **"VisRAG: Vision-based RAG on Multi-modality Documents" — Tang et al. (2025)**.
    - https://arxiv.org/html/2410.10594
    - Pure-vision RAG (no OCR)
    - 20-40% end-to-end improvement vs text RAG
    - Pre-trained on synthetic data

13. **"Hierarchical visual semantic guidance for relationship recognition in domain KGs" — Wang, Guo, Luo (2024)**.
    - https://doi.org/10.1016/j.engappai.2024.109040
    - Hierarchical visual guidance for KG relation extraction

14. **"ViSR-KGC: Visual Subgraph Reasoning with VLMs for MMKGC" (arxiv)**.
    - https://arxiv.org/html/2608.05833v2
    - VLM reasoning over subgraph images
    - Outperforms embedding-only KGC

---

### B.5 — Temporal Knowledge Graphs & RAG

15. **"Graphiti: Building Real-Time Knowledge Graphs for AI Agents"** (arxiv 2501.13956).
    - https://arxiv.org/abs/2501.13956
    - Temporal KG framework (Zep)
    - Validity windows, episodes, provenance

16. **"RAG Meets Temporal Graphs: Time-Sensitive Modeling for Evolving Knowledge" — Han et al. (2025)**.
    - https://arxiv.org/abs/2510.13590
    - Bi-level temporal graph ( TG-RAG )
    - Time-sensitive retrieval & incremental updates

17. **"MNEME: Temporal KG RAG for Personal Knowledge Management" (2026)**.
    - https://github.com/erolkuluslu/MNEME/
    - 7-layer RAG with temporal citations

---

### B.6 — Hierarchical RAG & KG Indexing

18. **"RAG with Hierarchical Knowledge (HiRAG)" — ACL 2025 (Findings)**.
    - https://aclanthology.org/2025.findings-emnlp.321.pdf
    - Unsupservised hierarchical indexing
    - 3-level context (global → bridge → local)

19. **"KG-Retriever: Hierarchical Knowledge Indexing for RAG" (arxiv 2412.05547)**.
    - https://arxiv.org/html/2412.05547v1
    - Hierarchical Index Graph (HIG)
    - Intra/inter-document connectivity

20. **"HyGRAG: Unified Context & Relation-Aware Hierarchical Graph RAG" (arxiv 2606.18075)**.
    - https://arxiv.org/html/2606.18075v1
    - LSH clustering; dynamic updates
    - +9.7% multi-hop accuracy

21. **"H2H² KG: Hierarchical Heterogeneous Knowledge Graph" — VDGR-RAG (2026)**.
    - https://arxiv.org/html/2608.07994v2
    - Directory-enhanced routing; multi-route retrieval
    - TOC-aware navigation

22. **"KET-RAG: Cost-Efficient Multi-Granular Indexing for Graph-RAG (KDD 2025)" — Huang et al.**.
    - https://dlnext.acm.org/doi/10.1145/3711896.3737012
    - Multi-level indexing (entity + document + community)
    - Cost-efficient GraphRAG

23. **"Allan-Poe: All-in-one Graph Index for Hybrid Search (GPU)" (arxiv 2511.00855)**.
    - https://arxiv.org/html/2511.00855v2
    - Unified semantic metric space
    - Dynamic fusion of dense/sparse/KG paths

---

### B.7 — Conflict Detection & Resolution

24. **"TruthfulRAG v5" — Saxena (2024).**
    - https://github.com/eeshsaxena/Conflict-Aware-Graph-RAG
    - 9 improvements over v4 baseline
    - Temporal decay; corroboration; adaptive entropy
    - arxiv:2511.10375 (baseline)

25. **"Knowledge Graph Fusion" — mcekikj (2025).**
    - https://github.com/mcekikj/knowledge-graph-fusion/
    - Bitemporal edges; ingest-time contradiction detection
    - Genuine contradiction handling (refuse vs resolve)
    - Effective-date scoping (`as_of`)

26. **"Conflict-Aware Temporal Memory" — HydraClaim (HydraDB).**
    - https://pypi.org/project/hydraclaim/
    - Graph-probe routing; bitemporal reads
    - Abstention when graph can't back answer

---

### B.8 — Hybrid Retrieval

27. **"Benchmarking Vector, Graph and Hybrid Retrieval" (arxiv 2507.03608)**.
    - https://arxiv.org/html/2507.03608v1
    - Comparative analysis of retrieval paradigms

28. **"VDGR-RAG" — Yan et al. (2026)**.
    - https://arxiv.org/html/2608.07994v2
    - Agentic GraphRAG; vector + directory + graph + reflection

---

## C. Real-Time Extraction References (Libraries)

| Library | Function | Paper/Source |
|---------|----------|-------------|
| **Docling** (IBM) | Layout analysis + OCR + table extraction | [arxiv 2408.09869](https://arxiv.org/abs/2408.09869) |
| **MinerU** | Complete doc parsing toolkit | [GitHub: opendatalab/MinerU](https://github.com/opendatalab/MinerU) |
| **Marker** | PDF → Markdown (OCR + layout) | [GitHub: VikParuchuri/marker](https://github.com/VikParuchuri/marker) |
| **Unstructured** | Parsing library (partition() API) | [unstructured.io](https://unstructured.io) |

---

## D. Standards & Protocols

| Standard | Use |
|----------|-----|
| **W3C PROV-O** | Provenance tracking (Semantica Provenance module) |
| **GDPR/HIPAA/SOX/FDA 21 CFR** | Compliance snapshots (Semantica change management) |
| **Apache Parquet** | Columnar data exchange |
| **JSON-LD** | Structured data export (CKS-MCP) |
| **SPARQL/RDF** | KG querying (Giannopoulou thesis) |

---

## E. Key Research Gaps (Not Yet Solved by Papers)

1. **Incremental VLM updates** — No paper covers re-enriching changed images during incremental intake.
   - Proposed workaround: Compare image hashes; re-run VLM only if changed.

2. **Cross-modal conflict resolution** — When image-extracted fact conflicts with text-extracted fact.
   - Proposed workaround: Use recency + confidence + authority scoring (context-graph's composite score).

3. **Multi-language document support** — Most extraction papers focus on English.
   - Proposed: Use multilingual VLM (Gemini 1.5 Pro) + language detection.

4. **Audio/video temporal alignment** — Aligning transcript timestamps with KG fact `valid_at`.
   - Proposed: Use Whisper word-level timestamps; store `segment_start`/`segment_end` metadata.

5. **ZIP bomb safety** — Limited academic work; engineering-only concern.
   - Proposed: Use AI-KE's archive-bomb limits (max ratio 100:1, max 500MB).

---

## F. How to Use These Papers (for Implementation/Research Teams)

1. **Cite in your proposal/spec** as supporting evidence for each component choice.
2. **For benchmarks**, use results from Table Extraction (Burdick et al.) and Multi-VIE (Li et al.).
3. **For temporal validity design**, cite Graphiti paper (Zep) + RAG Meets Temporal Graphs (Han et al.).
4. **For VLM enrichment**, cite Docs2KG (Sun et al.) + VisRAG (Tang et al.).
5. **For hierarchical indexing**, cite HiRAG (ACL 2025) + HyGRAG (arxiv 2606.18075).

---

## G. Quick Reference: Project → Method → Paper

| Project | Method | Supporting Paper |
|---------|--------|------------------|
| Graphiti | Temporal facts + episodes | Graphiti arxiv 2501.13956 |
| RAGBrain | Bi-temporal supersession | RAGBrain docs |
| Docling-Graph | VLM + schema-driven KG | Docs2KG (Sun et al., 2025) |
| Multi-VIE | Classification-guided LVLM | Li et al. (2026), Eng. App. AI |
| Diagram2Graph | Fine-tuned Qwen2.5-VL | Sujith S (2025) |
| VisRAG | Direct image embedding | Tang et al. (2025), VisRAG |
| VaLiK | Chain-of-Experts MMKG | Liu et al., ICCV 2025 |
| Docs2KG | Dual-path document parsing | Sun et al., ACM 2025 |
| Docling | Layout analysis + OCR | Ares Oliveira et al. 2018 |
| HiRAG | Hierarchical KG indexing | ACL 2025 Findings |
| Helix | LightRAG + Graphiti fusion | YashNuhash 2026 |
| Engram | Hybrid retrieval + temporal | Jamjet Labs 2025/26 |

---
---

## H. Open Research Questions for Human Validation

1. Should we **extend** Docs2KG's dual-path with our own VLM, or use Docling-Graph's VLM directly?
2. Do we need a **custom benchmark** for `samples5/` (domain-specific)? Suggested: derive from Docs2KG's evaluation (multi-metric: textual accuracy + reading order).
3. Should the **temporal validity** of audio/video extractions use `created_at` from metadata (when file was created), or `system ingested_at`? Recommend: hybrid (use metadata if available, fallback to ingest time, flag confidence).
4. Is there a paper that covers **incremental KG updates with VLM re-enrichment**? Currently none found — may need custom solution (hash-based image change detection).
5. Should we produce a **paper** ourselves summarizing this assembly? Strong candidate for academic publication (e.g., system demonstration at ACL/ICLR).
