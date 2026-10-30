# Temporal-Valid Knowledge Graph Retrieval-Augmented Generation for Stale Data Renewal and Uncertainty Detection in Decision Support

## Abstract
We study how decision support systems can maintain temporal validity across heterogeneous document streams so that commanders and analysts receive the most recent, authoritative facts with explicit uncertainty and provenance. The mini-extract system combines a bi-temporal Knowledge Graph with Retrieval-Augmented Generation and multiplex aggregation to track how information changes, detect conflicts across extraction paths, and surface current facts while preserving full audit trails.

## One-sentence description
How a decision support system uses various sources and tools/techniques so that any artifacts created are based on most recent information.

**Keywords:** temporal validity, knowledge graph, RAG, stale data, uncertainty, decision support, multiplex aggregation, semantic symbolic

## Project Type
System design and usability study

## Audience
Folks that make judgement, folks in general that want to be in the loop. Primary audience is military leaders and analysts who require the most recent data to make reliable decisions under time pressure. Secondary audience includes compliance officers and system designers who need auditability. If needs remain unmet, decisions are made on stale or conflicting data leading to erroneous outcomes and loss of trust in automated support.

## Introduction
In many operational settings there is a state where accurate temporal validity is not guaranteed. Decision support systems ingest many input data types — PDFs, spreadsheets, audio transcripts, images, multimedia — to create options for the commander. The right decision depends on the more relevant and most recent data, not on the oldest or the most frequently repeated.

The big problem is that what is being input into the system does not automatically surface as most relevant. Traditional extraction systems fail to account for the dynamic nature of information over time. When a file is modified, new information is distributed and old information becomes invalid and sometimes harmful. When files go through multiple extraction paths — text, OCR, VLM — they may produce conflicting interpretations of the same information, causing inconsistencies.

The concept is the research: can we design a system where every extracted fact carries explicit temporal metadata to prove its validity, where supersession is tracked, and where uncertainty is made explicit to the user. The engineering in the background — parsing, OCR, VLM — is expected.

We spotlight everything that goes good or bad in this research design, different from engineering design. Success is measured by whether users can reliably identify current facts, understand why an answer is current, and detect when information is uncertain or superseded.

## Approach

The experiment is conducted by building a mini-extractor that ingests most types of data and extracts information using various methods before aggregating information for user queries.

### Knowledge Graph and RAG
We use two complementary representations:

* **Knowledge Graph:** tracks every edit made to every file in the database while maintaining correctness based on latest input. It stores bi-temporal validity intervals, provenance, and supersession links. This is semantic and symbolic representation of facts with explicit relations and temporal attributes \cite{choi2025knowledge, sun2025docs2kg}.
* **Retrieval-Augmented Generation:** stores chunks of information within a vector index, retrieves most current information updated by the knowledge graph, before output to the user. Temporal filtering ensures only `current=true` facts are surfaced by default \cite{han2025ragtemporal, graphiti2025}.

### Multiplex Aggregation
Multiple extraction paths per document — native parsing, OCR, layout analysis, VLM enrichment — produce parallel fact sets. Multiplex aggregation fuses these paths using:
1. Entity resolution across paths
2. Confidence and authority scoring
3. Recency comparison via file modification timestamps
4. Conflict detection and most-recent-wins promotion

When conflicts arise, newer facts are promoted to true while older facts are demoted to history, with explicit supersession links.

### Files and Extraction
We use 6+ types of files to find staleness detection: PDF, DOCX, XLSX, audio, image/diagram, video. Each type has a different extraction method. The goal is to extract all information regardless of file type and maintain temporal lineage.

## Details
Trial + real experiments. Trial objectives: train subjects on how to read temporal validity indicators and uncertainty cues.

We use analysis by Sherman \cite{desjardins2017measuring} as a baseline for uncertainty communication, adapted to temporal validity rather than probability perception. The system will visualize range of temporal confidence and ask questions that help us identify whether users correctly interpret supersession and staleness cues.

## Evidence for Success
Why it will work: The system reuses production-grade open source components — Graphiti for temporal KG \cite{graphiti2025}, RAGBrain for bi-temporal supersession, Docling for multi-format extraction, Qwen2.5-VL for VLM enrichment \cite{sun2025docs2kg}. Temporal validity is enforced at schema level and retrieval defaults filter to current facts. Audit trails provide explainability.

## Best-case Impact Statement
In the best-case scenario: "We found that decision makers using a temporal-valid KG-RAG system can reliably identify the most recent facts, understand supersession and uncertainty, and make faster, more confident decisions with fewer errors from stale data."

## Major Milestones
* Set up schema to look for within various data types as well as extraction techniques to parse through them
* Have a working knowledge graph that shows edit history of a file once it is put into the model
* Prepare real-world files that are not biased towards the model to give real results against real files
* Having a valid RAG that has ability to go into its database and retrieve needed information
* Having the RAG and KG work together to make conflict resolutions and produce readable output with provenance

## Obstacles
Major obstacles:
* Slight modifications and exceptions to how data is presented
* Making a model that is universal for all types of data

Minor obstacles:
* Fighting inconsistencies in data using superseding capability of knowledge graph
* User misinterpretation of temporal flags and uncertainty cues

## Resources Needed
* Prolific account for usability study
* Access to representative military-style documents with version history
* Compute for VLM enrichment

## Related Work
Hullman et al. \cite{hullman2011impact} shows external factors influence visual perception of data.

Docs2KG \cite{sun2025docs2kg} provides unified Layout + Metadata + Semantic KG construction from heterogeneous documents with human-in-the-loop verification.

Graphiti \cite{graphiti2025} builds real-time knowledge graphs for AI agents with validity windows, episodes, provenance.

RAG Meets Temporal Graphs \cite{han2025ragtemporal} proposes bi-level temporal graph for time-sensitive retrieval and incremental updates.

TruthfulRAG \cite{saxena2024} addresses conflict-aware graph RAG with temporal decay and corroboration.

These works address temporal validity, conflict resolution, and multimodal extraction. Our contribution is the integration of multiplex aggregation with explicit temporal validity and usability evaluation for decision support.

## Define Success
Minimum for publishability:
* Enough data to draw conclusion, at least as many participants as in Sherman's study baseline
* Demonstrated temporal correctness ≥95% on synthetic versioned corpus
* Users can correctly identify current vs superseded facts in usability test
* System surfaces most recent information by default across three retrieval modes: Pure RAG, RAG+KG Validator, KG-only

## If everything was deleted and you had one sentence
We are studying how to design a temporal-valid knowledge graph RAG system with multiplex aggregation so users have the most recent, valid information and can understand information loss and uncertainty.

## Notes on Semantic and Symbolic
The KG provides symbolic representation with explicit entities, relations, and temporal attributes. RAG provides semantic retrieval over unstructured chunks. Multiplex aggregation bridges symbolic and semantic views to ensure consistency and temporal validity \cite{choi2025knowledge, sun2026unstructured}.

