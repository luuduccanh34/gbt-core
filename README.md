<p align="center">
  <img src="https://github.com/luuduccanh34/gbt-core/raw/main/assets/gbt-logo.jpeg" alt="GBT Logo" width="200" />
</p>

<h1 align="center">Graph Build Tool (GBT)</h1>

<p align="center">
  <strong>Enterprise-Grade Graph Data Transformation & Schema Management</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/gbt-core/"><img src="https://img.shields.io/pypi/v/gbt-core.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/gbt-core/"><img src="https://img.shields.io/pypi/pyversions/gbt-core.svg" alt="Python Versions"></a>
  <a href="https://github.com/luuduccanh34/gbt-core/blob/main/LICENSE"><img src="https://img.shields.io/github/license/luuduccanh34/gbt-core" alt="License"></a>
</p>

---

## 📖 What is GBT?

**Graph Build Tool (GBT)** is a transformative workflow framework designed specifically for graph databases (currently natively supporting **Neo4j**). Inspired by modern analytics engineering practices, GBT brings rigorous software engineering principles—such as declarative configurations, modularity, templatization, and version control—into graph data engineering.

**Core Purpose:** GBT empowers data engineers, graph developers, and analysts to build, maintain, and document graph schemas (DDL) and transform graph data (DML) reliably and efficiently. By defining your graph structures in declarative **YAML** and your transformations in templated **Cypher/SQL**, GBT reduces complexity and standardizes graph deployments across your organization.

---

## 🚀 Getting Started

### Installation

Install `gbt-core` utilizing `pip` or your favorite Python package manager. To include Neo4j connector capabilities, install with the `neo4j` extra:

```bash
pip install "gbt-core[neo4j]"
```

If you are using **Poetry** (as used in this repository):

```bash
poetry add "gbt-core[neo4j]"
```

### Quick Start

1. **Initialize a Project**: Set up your project structure. (See the `example/` directory for a reference structure including `gbt_project.yaml` and profile configurations).
2. **Define Models**: Create your node and relationship models inside the `models/` directory using `.sql`, `.cypher`, and `schema_*.yml` configuration schemas.
3. **Run Transformations**: Execute the CLI commands to parse, compile, and run your graph models:

```bash
gbt compile
gbt run --target neo4j
```

---

## 🏗 Architecture

GBT strictly decouples **Source Extraction** and **Destination Loading (Graph DB)**, heavily utilizing a locally compiled JSON Manifest as the Source of Truth.

<p align="center">
  <img src="https://github.com/luuduccanh34/gbt-core/raw/main/assets/architecture-flow.png" alt="Architecture Flow" width="800" />
</p>

---

## ✨ Key Features

- **Neo4j Native Integration**: A robust Bolt-protocol connector capable of handling complex network executions seamlessly.
- **DDL Engine**: Automated Schema Management supporting structural bounds and constraints defined purely in YAML configurations.
- **DML Engine**: Dynamic data manipulation supporting various materialization strategies including high-speed `UNWIND` **append**, strict **merge**, and surgical **delete**.
- **Jinja2 Templating**: Leverage robust macros (`.cypher.j2`) to build dynamic, reusable, and modular Cypher queries.
- **Memory-Safe Validation**: Built-in schema validation preventing corrupted typings (e.g., String to Integer) from crashing the Graph runtime.
- **Command Line Interface (CLI)**: Intuitive CLI application providing core commands like `gbt compile`, `gbt run`, and `gbt docs`.

---

## 📚 Documentation

For in-depth architectural overviews, Core Engine details, Data Validation protocols, and templating cheat sheets, please serve the unified docs locally via MkDocs:

```bash
gbt docs
```

*(You can also visit the official documentation website hosted on GitHub Pages once deployed).*

---

## 🔮 Future Roadmap

The journey doesn't stop here. The future framework enhancements include:

- **Multi-Graph Database Support**: Expanding connector capabilities to AWS Neptune, Memgraph, TigerGraph, and more.
- **Data Testing & Quality Checks**: Declarative runtime testing to enforce unique entity constraints and referential integrity.
- **Automated Data Lineage UI**: A visual dashboard to explore the dependency graphs (DAG) of the models and relationships.

---

## 🤝 Contributing & License

Contributions, issues, and feature requests are welcome! 
Feel free to check [issues page](https://github.com/luuduccanh34/gbt-core/issues).

This project is licensed under the terms of the **MIT** license.
