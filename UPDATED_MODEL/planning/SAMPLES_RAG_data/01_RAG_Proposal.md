---
format: html
---

# 01_RAG_Proposal.md – Independent RAG System Proposal

## Project Name
Independent RAG Retrieval & Deduction System (Parallel to Existing Knowledge Graph)

---

## 1. Restatement of Core Goal

**Build a RAG-based retrieval system that operates completely independently of the Knowledge Graph.**

The system must:
1. Ingest and analyse the **same source files** (`samples5/` directory or equivalent) **on its own**, without relying on any Knowledge Graph infrastructure.
2. Build its **own vector index** and perform **retrieval + generation** without consulting the Knowledge Graph.
3. Produce its **own set of deductions / extracted facts** from the documents, formatted in a schema that enables comparison with KG facts.

This creates a **parallel pipeline** that can be compared against the existing Temporal KG RAG system to detect inconsistencies and validate correctness.

---

## 2. Purpose & Comparison Workflow

### Why an Independent RAG System?
- **Validation**: The existing KG system may have biases or gaps in its extraction logic. An independent RAG provides a cross-check.
- **Consistency Auditing**: Fact deductions from two independent systems should align on objective data (prices, dates, counts). Divergences expose extraction errors, conflicts in source data, or interpretation inconsistencies.
- **Temporal Correctness**: Both systems use `extract.py` timestamps, enabling time-based conflict resolution.

### Comparison Workflow
```
[samples5/] → [Independent RAG Pipeline] → [RAG Deductions]
                                    ↓
                 [KG Facts] ← [Existing KG Pipeline] ← [samples5/]
                                    ↓
                 [Comparison Module] → Detect Inconsistencies
                                    ↓
        ┌─────────────────┐
        ▼                 ▼
[Auto-Resolution]    [Human Report + Escalation]
```

### Inconsistency Types
| Type | Definition | Example |
|------|-----------|---------|
| **Value Conflict** | Same entity/predicate, different values | KG: price=100, RAG: price=120 |
| **Missing Fact** | One system extracts a fact the other misses | KG: has invoice_5, RAG: missing |
| **Interpretation Conflict** | Same source text, different deduced facts | KG: "price is 100", RAG: "price is $100 USD" |
| **Temporal Conflict** | Same source, different `as_of` timestamps | KG: as_of=2024-09-01, RAG: as_of=2024-09-02 |

---

## 3. Inconsistency Detection & Resolution Mechanism

### 3.1 Detection Pipeline
1. **Alignment by Source & Entity**: Match RAG deductions with KG facts using `source_file_path`, `entity_id`, and `predicate`.
2. **Semantic Normalization**: Normalise values (e.g., "$100" → `100`, "USD" stripping) before comparison.
3. **Fuzzy Matching**: Use embeddings to detect semantic similarity of facts that may be phrased differently.

### 3.2 Automatic Resolution Rules
| Rule ID | Condition | Resolution Action | Priority |
|---------|-----------|-------------------|----------|
| R1 | Both systems agree (`value` match + `as_of` match) | **No action** (mark as ✓ consistent) | N/A |
| R2 | Same `source_file_path`, same `predicate`, **newer `as_of` in RAG** | **Prefer RAG** (temporal validity) | High |
| R3 | Same `source_file_path`, same `predicate`, **newer `as_of` in KG** | **Prefer KG** (temporal validity) | High |
| R4 | Conflicting values, same `as_of`, **RAG value is numeric and KG value is text** | **Prefer RAG** (structured > unstructured) | Medium |
| R5 | Conflicting values, same `as_of`, **KG value has explicit provenance chain** | **Prefer KG** (stronger audit trail) | Medium |
| R6 | Conflicting values, **no clear rule** | **Escalate to Human** (generate report) | Low |

### 3.3 Human Escalation Report
When automatic resolution fails, generate a structured report:
```markdown
### Inconsistency Report #<ID>
- **Entity**: `entity_1`  
- **Predicate**: `has_price`  
- **RAG Deduction**: `Product X price is 120` (`as_of`: 2024-10-01, `source`: samples5/invoices/INV-2024-003.pdf)  
- **KG Fact**: `Product X price is 100` (`as_of`: 2024-09-15, `source`: samples5/invoices/INV-2024-002.pdf)  
- **Conflict Type**: Value Conflict  
- **Resolution Attempt**: R2 (prefer newer) → **BLOCKED** (RAG timestamp invalid)  
- **Recommended Action**: Human verify INV-2024-003.pdf timestamp integrity  
- **Raw Text**: [Quoted excerpts from both sources]  
```
*Important*: **Pause system processing** until human decision is received.

---

## 4. Success Criteria
1. Independent RAG system ingests `samples5/` and produces deductions **without accessing KG endpoints**.
2. Both systems extract facts from overlapping sources, enabling **meaningful comparison**.
3. Comparison module detects **≥90% of planted inconsistencies** in test dataset.
4. Automatic resolution resolves **≥80% of inconsistencies** without human intervention.
5. Human reports for unresolvable conflicts include **source excerpts, timestamps, and recommended actions**.

---

## 5. Scope Boundaries

### In Scope
- Independent RAG ingestion pipeline (file → chunks → embeddings → vector index).
- Fact deduction/extraction from unstructured text, tables, and semi-structured data.
- Comparison module (RAG deductions vs. KG facts).
- Automatic resolution engine with configurable rules.
- Human-readable inconsistency report generation.

### Out of Scope (for this proposal)
- Modifications to existing Temporal KG system.
- New user interface for RAG (reuse Streamlit UI from KG, or CLI).
- Retraining or fine-tuning embedding models.
- Deployment/distributed scaling.

---

## 6. Next Stage

**Awaiting human validation** of this proposal before proceeding to **Stage 2 – Analyst** (`02_RAG_Requirements_Analysis.md`).

---
**Status**: Draft awaiting explicit human approval
