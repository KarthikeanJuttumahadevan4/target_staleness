def parse_query(q):
    q = q.lower()
    if "price" in q:
        return "entity_1", "has_text", "price"
    if "report" in q:
        return "entity_1", "has_text", "report"
    return "entity_1", "has_text", None
