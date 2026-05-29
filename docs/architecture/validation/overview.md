# Validation Engine Overview

The **Validation Engine** acts as the primary gatekeeper of the Graph Build Tool (GBT). To maintain strict graph integrity, data cannot flow freely from analytical sources into Neo4j without undergoing rigorous inspection. This layer ensures that all operational payloads strictly adhere to the business rules and constraints defined in your configurations before execution.

---

## The Philosophy of Graph Validation

Unlike traditional data warehouses where "schema-on-read" paradigms are acceptable, Graph Databases demand absolute structural precision (schema-on-write). A single miscast property (e.g., an integer saved as a string) can corrupt complex Cypher path traversals globally.

GBT tackles this through an active interception mechanism:
1. **Intercept Batch Storage:** Halts data streams locally in physical memory.
2. **Evaluate Contracts:** Scans each node/relationship row against explicit YAML assertions.
3. **Execute Resolution Strategy:** Corrects, bypasses, or violently fails depending on the configured safety rules.

## Validation Modules

Currently, the Validation Engine delegates its responsibilities to specialized validation sub-engines to ensure separation of concerns.

| Component | Responsibility Scope | Status | Link |
| :--- | :--- | :--- | :--- |
| **Data Type Enforcement** | Guarantees physical memory types (Strings, Integers, Booleans, ISO 8601 Dates) map precisely to backend expectations. | ✅ Active | [Explore Data Type Validation](data-type.md) |
| **Contract Checks** | (Coming Soon) Validates complex entity constraints like row-level bounds or referential integrity. | 🕒 Planned | - |

> **Strategic Note:** All validation processes are entirely synchronous and occur micro-batch by micro-batch within the active pipeline, rather than functioning as post-hoc auditing tests. Your graph backend will never ingest a corrupted batch.

For a comprehensive guide on how variables are cast and error handling strategies are routed, please proceed to [Data Type Validation](data-type.md).
