# Quickstart

This guide will walk you through setting up a new GBT project, understanding its structure, and executing your first data pipeline.

## 1. Project Structure

A typical GBT project requires a specific directory structure to organize your models, schema configurations, and connection properties. Below is an example structure:

```text
example_project/
├── gbt_project.yaml
├── profiles.yaml
├── macros/
├── scripts/
├── plugin/
└── models/
    └── neo4j/
        ├── nodes/
        │   ├── customer.sql
        │   ├── package.sql
        │   └── schema/
        │       ├── schema_customer.yml
        │       └── schema_package.yml
        └── relationship/
            ├── orders.sql
            └── schema/
                └── schema_package_purchase.yaml
```

### Essential Configurations

- **`gbt_project.yaml`**: The main configuration file for your project. It defines the project identity, metadata, and global directory mappings (e.g., where to find `models`, `macros`, etc.).
- **`profiles.yaml`**: Stores your database connection configurations, including credentials for your Source (e.g., Trino) and Destination (e.g., Neo4j). *Ensure you never commit sensitive passwords to version control!*
- **`models/`**: The heart of your project. This directory contains `.sql` (or `.cypher`) files used to define the logic for extracting data from your source platform.
- **`schema/` (.yaml/.yml)**: Found closely embedded inside your model folders, these `.yaml` files dictate the definition and behavior of your Graph elements (Nodes and Relationships). It manages properties mapping, data types (contracts), and rules (e.g., explicit constraints and indexes).

## 2. Environment Setup

Before running GBT, ensure that you have configured the environment variables required to authenticate and connect to your databases. You can export them directly in your terminal session or define them in an `.env` file at the root of your project.

Here is an `.env` example mapping the required credentials for Trino (Source) and Neo4j (Destination):

```env
# Neo4j Connection Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# Trino Connection Configuration
TRINO_HOST=https://localhost
TRINO_PORT=8443
TRINO_USER=admin
TRINO_PASSWORD=admin
TRINO_CATALOG=default
TRINO_SCHEMA=default
```

## 3. Compiling the Project

Before running queries against the database, you can dry-run and compile the model scripts using the `compile` command. This step parses your templates, manifests, and constraint models, writing the output Cypher and SQL scripts to a local `target/` directory:

```bash
gbt compile --select customer
```

## 4. Running Models

To execute the data injection flow (Loader) into Neo4j, use the `run` command. 

```bash
# Run a specific model conditionally/incrementally
gbt run --select customer

# Force a full refresh (drops the graph object entirely and recreates it with new constraints/data)
gbt run --select customer --full-refresh
```
During execution, GBT will parse connections, load manifests, build schema constraints dynamically, validate records strictly according to your target layout, and stream blocks of appended records to the database.

## 5. Explore Documentation

Want to read this very documentation offline or share it securely with your team? GBT ships with a built-in web server to browse beautiful project documents!

Simply run:

```bash
gbt docs
```
And navigate to [http://localhost:3401](http://localhost:3401) in your browser!
