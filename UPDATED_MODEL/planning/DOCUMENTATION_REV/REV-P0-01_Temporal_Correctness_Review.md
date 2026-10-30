---
format: html
---

# REV-P0-01 Implementation Specification - Temporal Correctness Review

## Ticket Summary
Priority: P0
Title: Temporal Correctness Review
Goal: Review conflict resolution, current flag enforcement, retrieval filters.

## Review Checklist

- [ ] ConflictResolver implements most-recent-wins correctly
- [ ] Current flag invariant maintained after promotion/demotion
- [ ] Pure RAG filters by current=true
- [ ] KG-only queries include current=true
- [ ] RAG+KG validator overrides with KG current fact
- [ ] Supersedes edges created correctly
- [ ] Explainability requirement met

## Review Report Template

```markdown
## Review Findings
...
## Sign-off
Temporal correctness: APPROVED / REJECTED
```

Status: Ready for review
