from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j","password"))
with driver.session() as s:
    rows = s.run("MATCH (f:Fact) RETURN f.fact_id AS id, f.subject_entity_id AS s, f.predicate AS p, f.object_value AS v, f.current AS c, f.as_of AS a LIMIT 20")
    for r in rows:
        print(dict(r))
driver.close()
