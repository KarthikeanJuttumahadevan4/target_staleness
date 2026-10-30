---
format: html
---

# Design Documents

This directory contains all design documentation for the Universal File Metadata & Version History Extractor.

---

## Current Documents

| File | Purpose |
|------|---------|
| `PROPOSAL.md` | Original project proposal |
| `SPECS.md` | Technical specifications |
| `IMPLEMENTATION_ROADMAP.md` | Implementation plan |

---

## Document Guide

### PROPOSAL.md
- **What**: Original project proposal
- **Why**: Defines the problem, vision, and high-level goals
- **When to Read**: Before starting development

### SPECS.md
- **What**: Technical specifications
- **Why**: Detailed requirements, edge cases, and error handling
- **When to Read**: During development to understand requirements

### IMPLEMENTATION_ROADMAP.md
- **What**: Step-by-step implementation plan
- **Why**: Phased approach with milestones
- **When to Read**: To understand the development timeline

---

## Creating New Design Documents

When adding new design documents:

1. **Naming**: Use UPPERCASE.md naming (e.g., AUTHENTICATION.md, CACHING.md)
2. **Structure**: Include purpose, scope, technical details, and examples
3. **Location**: Place in this directory

---

## Design Principles

The system follows these core design principles:

1. **Multi-Model Extraction**: Use multiple extraction methods per file type for maximum data retrieval
2. **Minimal Confidence Assumptions**: Assign evaluation bands (high/medium/low) to every extracted fact
3. **Unified Output**: All file types produce consistent JSON output format
4. **Extensibility**: Easy to add new file types and extraction methods
5. **Transparency**: Track source of every extracted fact
6. **Performance**: Batch processing and caching for efficient operation

---

## Quick Navigation

```bash
# List all design documents
ls -la prototype/design/

# View a document
cat prototype/design/PROPOSAL.md

# Search across all design documents
grep -r " Knowledge Graph " prototype/design/
```
