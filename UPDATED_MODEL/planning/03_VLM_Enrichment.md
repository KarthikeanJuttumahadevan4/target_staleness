---
format: html
---

# 03_VLM_Enrichment — Visual Content Enrichment

## Purpose

Enrich extracted facts with **visual context** (charts, diagrams, flowcharts,
tables, images) using VLMs, ensuring complete information capture from
non-textual document elements.

---

## VLM Projects to Assemble

### 1. Docling-Graph (Primary)
- **Repo:** [github.com/docling-project/docling-graph](https://github.com/docling-project/docling-graph)
- **Developed by:** Docling Team (IBM Research)
- **License:** MIT
- **Models:** Any backend (Ollama, vLLM, OpenAI, Anthropic, Mistral)
- **Use case:** Schema-driven extraction from any document
- **Output:** Pydantic → NetworkX (nodes + edges + provenance)
- **Key feature:** Deterministic data grounding (no extra LLM calls)

### 2. Diagram2Graph (Specialized: Flowcharts)
- **Repo:** [github.com/sujiths/diagram2graph](https://dev.to/sujiths/diagram2graph-...)
- **Developed by:** Sujith S (community)
- **License:** Apache 2.0
- **Model:** Fine-tuned Qwen2.5-VL-3B (PEFT/LoRA)
- **Benchmarks:** Node F1 +14.2% (89.1%), Edge F1 +23.4% (69.45%)
- **Use case:** Technical diagrams, architecture diagrams, flowcharts
- **Output:** Neo4j-compatible JSON (nodes + edges)

### 3. Multi-VIE (Specialized: Forms/Certificates)
- **Repo:** [github.com/FairmeHIT/Multi-VIE](https://github.com/FairmeHIT/Multi-VIE)
- **Developed by:** Huafu Li, Guo Chen, Jia Xia, et al. (HIT)
- **License:** MIT (code); Apache 2.0 (model)
- **Model:** Qwen2.5-VL-7B-SFT
- **Benchmarks:** 93.65% F1 on multi-type extraction (16 certificate types)
- **Use case:** Forms, invoices, contracts, certificates, official documents
- **Output:** Structured JSON with type-specific landmarks

### 4. VaLiK (Multimodal KG Construction)
- **Repo:** [github.com/Wings-Of-Disaster/VaLiK](https://github.com/Wings-Of-Disaster/VaLiK)
- **Developed by:** Junming Liu, Siyuan Meng, et al. (ICCV 2025)
- **License:** MIT
- **Method:** Chain-of-Experts VLM pipeline
- **Use case:** Annotation-free MMKG construction from images
- **Output:** Direct entity-to-image linkage, knowledge graph

### 5. VisRAG (Visual Retrieval)
- **Repo:** [github.com/openbmb/visrag](https://github.com/openbmb/visrag)
- **Developed by:** OpenBMB / Tsinghua University
- **License:** Apache 2.0
- **Model:** VisRAG-Ret (VLM-based retriever)
- **Use case:** Direct image embedding (bypass OCR loss)
- **Benchmarks:** 20-40% end-to-end improvement vs text-based RAG

---

## VLM Enrichment Pipeline

```
Extracted Document
       │
       ├── [Text-only regions] ──► Skip (already text-extracted)
       │
       ├── [Tables detected] ──► Docling table structure model
       │                          └──► Table cells → KG facts
       │
       ├── [Charts/graphs detected] ──► Qwen2.5-VL-7B caption
       │                               └──► Caption → NER → facts
       │
       ├── [Flowcharts/diagrams] ──► Diagram2Graph (fine-tuned VLM)
       │                              └──► Nodes + edges → KG
       │
       ├── [Forms/certificates] ──► Multi-VIE (Qwen2.5-VL-7B-SFT)
       │                            └──► Landmarks → KG facts
       │
       └── [Images without OCR text] ──► Multi-VIE / GPT-4o Vision
                                        └──► Captions → NER → facts
```

---

## Models to Use

### Local (No API Cost, Self-Hosted)
| Model | Size | Best For | Hardware |
|-------|------|---------|----------|
| **Qwen2.5-VL-7B-SFT** (Multi-VIE) | 7B | Forms, certificates, tables | 16GB VRAM |
| **Qwen2.5-VL-3B** (Diagram2Graph) | 3B | Diagrams, flowcharts | 8GB VRAM |
| **MiniCPM-V-2.6** | 8B | General VLM | 16GB VRAM |

### Cloud (Higher Quality, Pay-Per-Use)
| Model | Best For | Cost |
|-------|---------|------|
| **GPT-4o Vision** | Complex diagrams, multi-language | $$ |
| **Gemini 1.5 Pro** | Long documents, 1M context | $$ |
| **Claude 3.5 Sonnet** | Detailed analysis, reasoning | $$ |

---

## Provenance Tagging in VLM Enrichment

Every VLM-extracted fact gets:

```json
{
  "content": "Revenue increased by 15% in Q3 2024",
  "source_image": "samples5/report.pdf/page_5.png",
  "extraction_path": "vlm",
  "model_used": "Qwen2.5-VL-7B-SFT",
  "confidence": 0.92,
  "bbox": [100, 200, 300, 50],
  "timestamp": "2024-01-15T10:30:00Z",
  "as_of": "2024-01-15T10:30:00Z",
  "current": true
}
```

---

## Open Questions

1. Should VLM run **synchronously** during intake (slows pipeline) or **async background**?
2. For diagrams, should we accept Diagram2Graph output directly, or re-verify with a second VLM?
3. What's the confidence threshold to reject VLM extractions (currently proposed: 0.7)?
4. Should we VLM-enrich every image, or only those with no accessible alt-text?
