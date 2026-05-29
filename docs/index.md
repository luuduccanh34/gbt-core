# Welcome to GBT Core

Welcome to the official documentation for **Graph Build Tool (GBT)**! 

<p align="center">
  <em>An enterprise-grade, configuration-driven ETL framework purpose-built for Graph Databases.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/gbt-core/" target="_blank">PyPI Package</a> &nbsp;|&nbsp;
  <a href="https://github.com/luuduccanh34/gbt-core/tree/main" target="_blank">GitHub Repository</a>
</p>

---

## Overview

**GBT (Graph Build Tool)** is a powerful data engineering pipeline designed to streamline the process of building, managing, and transforming graph data models. Whether you are dealing with complex relational networks, knowledge graphs, or fraud detection systems, GBT provides a declarative approach to graph database operations.

GBT operates on two primary foundational pillars:

### 1. Loader
The **Loader** engine is the primary mechanism for ingesting data. It allows data engineers to extract records from diverse analytical data sources and load them directly into your target Graph Database. 
- **Configuration-Driven:** Uses simple, intuitive YAML configurations combined with SQL/Cypher definitions.
- **Contract Enforcement:** Provides data type schema validation, explicit constraint mapping, and index handling automatically.
- **Adaptive Execution:** Supports robust `Incremental` and `Full Refresh` modes seamlessly integrated into your workflow.

### 2. Transformer (Coming Soon)
The **Transformer** engine will focus on in-database transformations. It will allow users to define complex graph algorithms, multi-hop relationship building, and node properties aggregation natively inside the Graph Database without pulling massive subsets of data back out into memory. 

---

## Current Support Matrix

GBT is architected to be modular and highly extensible. In the current release, we officially support the following core components:

| Component | Supported Integration | Status |
| :--- | :--- | :--- |
| **Source** (Extraction) | **Trino** | `Stable` |
| **Destination** (Graph DB) | **Neo4j** | `Stable` |

*Note: The architecture supports rapid implementation of new source SQL engines and Graph Database destinations in future updates.*

---

## Key Capabilities

- **Automated Schema Definition (DDL):** Builds, asserts, and manages complex constraint layers.
- **Native Multi-Type Modeling:** Perfectly handles structural nuances between independent `Nodes` and interconnected `Relationships`.
- **Dependent Manifest Tree:** Computes logical dependency graphs matching execution processes efficiently.
- **Beautiful CLI Telemetry:** Enterprise-grade output monitoring tracked with timers and granular execution logs.

---

**Ready to unleash the power of Graphs?** Jump over to the [Getting Started Guide](getting-started/installation.md) to kick off your first project!
