from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j","password"))
with driver.session() as s:
    s.run("CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE")
    s.run("CREATE CONSTRAINT fact_id_unique IF NOT EXISTS FOR (f:Fact) REQUIRE f.fact_id IS UNIQUE")
    s.run("CREATE CONSTRAINT provenance_id_unique IF NOT EXISTS FOR (p:Provenance) REQUIRE p.provenance_id IS UNIQUE")
print("Schema applied")
driver.close()
