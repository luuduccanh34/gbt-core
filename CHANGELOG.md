# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-05-29

### Changed
- **Dependency Management (Fat Framework Architecture)**: 
  - Restructured `pyproject.toml` to promote core connectors (`Trino`, `Postgres`, `Neo4j`) from Optional Dependencies to Default Dependencies. 

## [0.1.2] - 2026-05-29

### Added
- **Trino Connector**: Full support for Trino connector, allowing GBT to extract data efficiently from distributed data warehouses.
- **Data Execution Modes**: Added support to run both Incremental and Full-Refresh DML loads from Trino sources directly into Neo4j graph destinations.
- **Documentation Server**: Introduced the `gbt docs` CLI command to compile and serve Mkdocs-based documentation locally with dynamic architecture flows.
- **Validation Engine**: Added `ValidationManager` and `TypeCaster` to actively validate raw payloads, type-cast physical memory objects, and trap schema errors via strategic configurations (`fail`, `nullify`, `skip_row`).
- **Core Engine Separation**: Completely decoupled the engine architecture into `Source` (Extraction via Trino) and `Destination` (Graph processing via Neo4j) to optimize system scalability.
- **Inspector Engine (Neo4j)**: Advanced System Meta Scanning (`InspectorEngine`) added to dynamically fetch and map auto-generated system constraints and index metadata.
- **Relationship DML Support**: Added Jinja templates and engine directives (`append_relation`, `delete_relation`) for creating and severing physical directional edges between nodes.
- **CLI Upgrades**: Enhanced output interfaces using the `rich` library to render animated execution spinners and professional log tracking during `gbt run`.

### Changed
- **Folder Restructure**: Reorganized internal templates (`ddl`, `dml`) into database-specific paths (`destinations/neo4j/*`) to support future multi-graph platform expansion.

## [0.1.1] - 2026-05-23

### Changed
- **Documentation**: Updated `README.md`.
- **Installation**: Modified installation instructions to specify the `neo4j` extra (i.g., `pip install "gbt-core[neo4j]"`) for correct dependency resolution.

## [0.1.0] - 2026-05-23

### Added
- **Neo4j Connectivity**: Initiated support to establish connections to Neo4j graph databases seamlessly using project configuration profiles.
- **Schema Builder (DDL)**: Added schema management capabilities to execute declarative rules, such as creating constraints natively in Neo4j.
- **Model Compilation & Execution (DML)**: 
  - Ability to fully compile Cypher models from the workspace.
  - Ability to run compiled Cypher models dynamically, with support for targeting specific models and specific databases.
