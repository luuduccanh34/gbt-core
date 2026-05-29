# Template Engine Reference & Cheat Sheet

The **Template Engine** sits at the execution frontier of GBT. Instead of hard-coding raw database commands, GBT utilizes robust [Jinja2](https://jinja.palletsprojects.com/) macros (`.cypher.j2` or `.sql.j2`) to translate dynamic configurations directly into high-performance, native database queries.

This document serves as the official **Cypher Cheat Sheet & GBT Support Matrix**. It outlines common Graph Database operations (specifically Cypher for Neo4j) and details their structural support within the GBT Framework.

---

## 1. GBT Neo4j Support Matrix

Below is a comprehensive matrix of common Cypher commands and their current support status within GBT's template engine.

| Operation Type | Cypher Command | GBT Status | GBT Internal Template |
| :--- | :--- | :--- | :--- |
| **Nodes** | `CREATE (n)` / `UNWIND ... CREATE` | ✅ Supported | `append_node.cypher.j2` |
| | `MERGE (n)` / `UNWIND ... MERGE` | ✅ Supported | `merge_node.cypher.j2` |
| | `MATCH (n) SET n.prop = ...` | ❌ Not Supported | - |
| | `DETACH DELETE n` | ✅ Supported | `delete_node.cypher.j2` |
| | `REMOVE n:Label` | ✅ Supported | `delete_label.cypher.j2` |
| **Relationships** | `CREATE ()-[r]->()` | ✅ Supported | `append_relation.cypher.j2` |
| | `MERGE ()-[r]->()` | ❌ Not Supported | - |
| | `DELETE r` | ✅ Supported | `delete_relation.cypher.j2` |
| **Schema (DDL)** | `CREATE CONSTRAINT` | ✅ Supported | `create_constraint.cypher.j2` |
| | `DROP CONSTRAINT` | ✅ Supported | `delete_constraint.cypher.j2` |
| | `CREATE INDEX` | ❌ Not Supported | - |
| | `DROP INDEX` | ❌ Not Supported | - |
| **Metadata** | `SHOW CONSTRAINTS YIELD *` | ✅ Supported | `show_constraints.cypher.j2` |
| | `SHOW INDEXES YIELD *` | ❌ Not Supported | - |

---

## 2. Supported Template Cheat Sheet

All officially supported templates for **Neo4j** reside under the `/core/gbt/templates/destinations/neo4j` path. They are scientifically split across three standard databases operations: **DDL**, **DML**, and **META**.

### A. Data Definition Language (`/ddl`)

These templates strictly define the non-data, structural boundaries of the graph.

| Template Name | Jinja Inputs Required | Executable Output Pattern |
| :--- | :--- | :--- |
| `create_constraint.cypher.j2` | `constraint_name`<br>`model_type`<br>`label_or_type`<br>`property_name`<br>`rule` | `CREATE CONSTRAINT {name} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} {rule};` |

> **Context:** Used dynamically by the `SchemaBuilderEngine` when `properties` with explicit constraints (like `IS UNIQUE`) are discovered inside `schema_*.yml`.

<br>

### B. Data Manipulation Language (`/dml`)

These are heavily parameterized bulk templates designed to mutate massive scales of Node or Relationship records.

**1. Appending Operations**

| Template Name | Jinja Inputs Required | Operational Context |
| :--- | :--- | :--- |
| `append_node.cypher.j2` | `node_label`, `properties` | Bulk inserts independent Nodes via Cypher `UNWIND`. |
| `merge_node.cypher.j2` | `node_label`, `key_properties`, `set_properties` | Safely merges (upserts) Nodes ensuring no duplicates based on unique keys. |
| `append_relation.cypher.j2` | `source_label`, `source_key`, `source_ref`<br>`target_label`, `target_key`, `target_ref`<br>`physical_name`, `properties` | Connects source to target Nodes efficiently using isolated matches. |

**2. Wiping & Deletions**

These templates are critical for `--full-refresh` operations where surgical precision guarantees system safety.

| Template Name | Executable Mechanism |
| :--- | :--- |
| `delete_node.cypher.j2` | Utilizes `DETACH DELETE n IN TRANSACTIONS OF 1000 ROWS` preventing dead-locks and memory bottlenecks. |
| `delete_relation.cypher.j2` | Utilizes `DELETE r IN TRANSACTIONS OF 10000 ROWS` ensuring massive network wipes fastly. |
| `delete_constraint.cypher.j2` | Executes precise `DROP CONSTRAINT {constraint_name} IF EXISTS;`. |
| `delete_label.cypher.j2` | Strips metadata tags silently via `MATCH (n:{label}) REMOVE n:{label}`. |

<br>

### C. System Metadata (`/meta`)

These templates do not insert or destroy data; they serve as tactical reconnaissance tools helping internal engines chart the physical database territory.

| Template Name | Executable Context |
| :--- | :--- |
| `show_constraints.cypher.j2` | Fetches auto-generated constraint IDs dynamically: `SHOW CONSTRAINTS YIELD * WHERE '{node_label}' IN labelsOrTypes RETURN name;` |
