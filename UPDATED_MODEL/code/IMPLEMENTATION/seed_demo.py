from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j","password"))
with driver.session() as s:
    s.run("""
    MERGE (e:Entity {entity_id:"entity_1"})
    MERGE (p:Provenance {provenance_id:"prov_demo", source_file_path:"samples5/demo/price.txt", as_of:datetime("2024-10-15T20:00:00Z")})
    MERGE (f:Fact {fact_id:"fact_1", subject_entity_id:"entity_1", predicate:"has_text", object_value:"Product X price is 120", current:true, as_of:datetime("2024-10-15T20:00:00Z")})
    MERGE (e)-[:HAS_FACT]->(f)
    MERGE (f)-[:HAS_PROVENANCE]->(p)
    """)
print("seeded")
driver.close()
