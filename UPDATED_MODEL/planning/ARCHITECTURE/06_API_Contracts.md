# 06_API_Contracts — Internal Interfaces

## Intake

```python
def submit(path: str) -> JobID
def process_job(job: Job) -> IntakeResult
```

## Extraction

```python
def extract(path: str) -> NormalizedExtract
```
NormalizedExtract includes: text, entities, relations, ingest_method,
as_of, model_used, provenance.

## KG

```python
def ingest_fact(extract: NormalizedExtract) -> list[FactID]
def query_facts(entity_id, predicate, as_of=None, current_only=True) -> list[Fact]
def get_supersession_chain(fact_id) -> list[Fact]
def snapshot() -> SnapshotID
```

## Retrieval

```python
def pure_rag(q: str, k: int, as_of=None) -> RetrievalResult
def rag_kg_validator(q: str, k: int, as_of=None) -> RetrievalResult
def kg_only(q: str, hops: int, as_of=None) -> RetrievalResult
```

## Generation

```python
def answer(q: str, facts: list[RetrievedFact], mode: str) -> AnswerResponse
```
AnswerResponse: answer, facts (cited), confidence, audit_id.

## Errors / Exit Codes (CLI shim)
- 0 success; 1 usage error; 2 scanned/unsupported/failed.
- All failures return structured JSON in stdout with `notes`.
