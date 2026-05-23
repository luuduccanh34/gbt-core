# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-23

### Added
- **Neo4j Connectivity**: Initiated support to establish connections to Neo4j graph databases seamlessly using project configuration profiles.
- **Schema Builder (DDL)**: Added schema management capabilities to execute declarative rules, such as creating constraints natively in Neo4j.
- **Model Compilation & Execution (DML)**: 
  - Ability to fully compile Cypher models from the workspace.
  - Ability to run compiled Cypher models dynamically, with support for targeting specific models and specific databases.
