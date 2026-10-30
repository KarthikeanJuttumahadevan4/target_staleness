#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
from src.temporal.timestamp_extractor import TimestampExtractor
from src.extraction.multi_path_extractor import MultiPathExtractor
from src.enrichment.vlm_enrichment import VLMEnricher
from src.temporal.temporal_kg import TemporalKG
from src.temporal.conflict_resolver import ConflictResolver as BaseResolver

class ConflictResolver(BaseResolver):
    def upsert_fact_with_resolution(self, fact_id, subject_entity_id, predicate, object_value, as_of, provenance_id, source_file_path):
        if isinstance(as_of, str):
            as_of_dt = datetime.fromisoformat(as_of.replace("Z","+00:00"))
        else:
            as_of_dt = as_of
        self.kg.upsert_fact(fact_id, subject_entity_id, predicate, object_value, as_of_dt, provenance_id)
        olds = self.kg.get_current_facts(subject_entity_id, predicate)
        if olds:
            old = olds[0]
            if old.get("fact_id") != fact_id:
                def parse(v):
                    if isinstance(v, datetime):
                        return v
                    if isinstance(v, str):
                        return datetime.fromisoformat(v.replace("Z","+00:00"))
                    return None
                old_as_of = parse(old.get("as_of"))
                if old_as_of and as_of_dt > old_as_of:
                    self.kg.mark_superseded(old.get("fact_id"), fact_id, as_of_dt)

base = Path("samples5")
extractor = TimestampExtractor()
multi = MultiPathExtractor()
enricher = VLMEnricher()
kg = TemporalKG("bolt://localhost:7687","neo4j","password")
resolver = ConflictResolver(kg)

count = 0
for p in base.rglob("*"):
    if p.is_file() and p.suffix.lower() in [".txt",".pdf",".docx",".xlsx",".pptx"]:
        as_of, _ = extractor.get_as_of(p)
        raw_facts = multi.extract(p)
        for rf in raw_facts:
            norm = enricher.enrich([rf])[0]
            fact_id = f"{p.stem}_{hash(rf.text) & 0xffffffff}"
            resolver.upsert_fact_with_resolution(
                fact_id=fact_id,
                subject_entity_id=norm["subject_entity_id"],
                predicate=norm["predicate"],
                object_value=norm["object_value"],
                as_of=as_of,
                provenance_id=rf.provenance_id,
                source_file_path=str(p)
            )
            count += 1
print(f"Ingested {count} facts from samples5/")
