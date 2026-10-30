#!/usr/bin/env python3
from datetime import datetime
from src.temporal.temporal_kg import TemporalKG

class ConflictResolver:
    def __init__(self, kg):
        self.kg = kg
    def upsert_fact_with_resolution(self, fact_id, subject_entity_id, predicate, object_value, as_of, provenance_id, source_file_path):
        existing = self.kg.get_current_facts(subject_entity_id, predicate)
        if not existing:
            self.kg.upsert_fact(fact_id, subject_entity_id, predicate, object_value, as_of, provenance_id)
            return {"action":"inserted"}
        old = existing[0]
        old_as_of = datetime.fromisoformat(old.get("as_of","").replace("Z","+00:00"))
        if as_of > old_as_of:
            with self.kg.driver.session() as s:
                s.run("MATCH (f:Fact {fact_id:$id}) SET f.current=false", id=old["fact_id"])
            self.kg.upsert_fact(fact_id, subject_entity_id, predicate, object_value, as_of, provenance_id)
            return {"action":"promoted"}
        return {"action":"demoted"}
