"""
Knowledge graph builder/query layer backed by Neo4j.

Nodes: Equipment, Engineer, Inspection, Maintenance, Plant, Document,
       Incident, Regulation
Relationships: CONNECTED_TO, FAILED_DUE_TO, MAINTAINED_BY, MENTIONED_IN,
       LOCATED_AT, GENERATED_FROM
"""
from neo4j import GraphDatabase
from app.config import get_settings

settings = get_settings()

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    return _driver


def close_driver():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


def ensure_constraints():
    query = """
    CREATE CONSTRAINT equipment_tag IF NOT EXISTS FOR (e:Equipment) REQUIRE e.tag IS UNIQUE;
    """
    with get_driver().session() as session:
        for stmt in query.strip().split(";"):
            if stmt.strip():
                session.run(stmt)


def upsert_document_node(document_id: str, filename: str, category: str, plant: str | None):
    query = """
    MERGE (d:Document {id: $document_id})
    SET d.filename = $filename, d.category = $category
    WITH d
    FOREACH (_ IN CASE WHEN $plant IS NULL THEN [] ELSE [1] END |
        MERGE (p:Plant {name: $plant})
        MERGE (d)-[:LOCATED_AT]->(p)
    )
    """
    with get_driver().session() as session:
        session.run(query, document_id=document_id, filename=filename, category=category, plant=plant)


def upsert_equipment_from_entities(document_id: str, entities: list[dict], plant: str | None):
    """
    Given extracted entities for a document, create/update Equipment,
    Engineer nodes and link them to the source Document with
    MENTIONED_IN / GENERATED_FROM relationships.
    """
    equipment_tags = [e["entity_value"] for e in entities if e["entity_type"] == "EQUIPMENT_ID"]
    engineers = [e["entity_value"] for e in entities if e["entity_type"] == "ENGINEER"]
    failures = [e["entity_value"] for e in entities if e["entity_type"] == "FAILURE_REASON"]

    with get_driver().session() as session:
        for tag in equipment_tags:
            session.run(
                """
                MERGE (e:Equipment {tag: $tag})
                WITH e
                MATCH (d:Document {id: $document_id})
                MERGE (e)-[:MENTIONED_IN]->(d)
                """,
                tag=tag, document_id=document_id,
            )
            for reason in failures:
                session.run(
                    """
                    MATCH (e:Equipment {tag: $tag})
                    MERGE (i:Incident {reason: $reason, document_id: $document_id})
                    MERGE (e)-[:FAILED_DUE_TO]->(i)
                    """,
                    tag=tag, reason=reason[:200], document_id=document_id,
                )
        for eng in engineers:
            session.run(
                """
                MERGE (p:Engineer {name: $name})
                WITH p
                MATCH (d:Document {id: $document_id})
                MERGE (p)-[:GENERATED_FROM]->(d)
                """,
                name=eng, document_id=document_id,
            )
            for tag in equipment_tags:
                session.run(
                    """
                    MATCH (p:Engineer {name: $name})
                    MATCH (e:Equipment {tag: $tag})
                    MERGE (e)-[:MAINTAINED_BY]->(p)
                    """,
                    name=eng, tag=tag,
                )


def fetch_graph(limit: int = 300) -> dict:
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    LIMIT $limit
    """
    nodes = {}
    edges = []
    with get_driver().session() as session:
        result = session.run(query, limit=limit)
        for record in result:
            n, r, m = record["n"], record["r"], record["m"]
            for node in (n, m):
                node_id = str(node.element_id)
                if node_id not in nodes:
                    label = list(node.labels)[0] if node.labels else "Node"
                    display = node.get("tag") or node.get("name") or node.get("filename") or node.get("reason") or node_id
                    nodes[node_id] = {"id": node_id, "label": display, "type": label, "properties": dict(node)}
            edges.append({
                "source": str(n.element_id),
                "target": str(m.element_id),
                "relationship": r.type,
            })
    return {"nodes": list(nodes.values()), "edges": edges}
