#!/usr/bin/env python3
class VLMEnricher:
    def enrich(self, raw_facts):
        normalized = []
        for f in raw_facts:
            normalized.append({
                "subject_entity_id": "entity_1",
                "predicate": "has_text",
                "object_value": f.text[:200],
                "provenance_id": f.provenance_id
            })
        return normalized
