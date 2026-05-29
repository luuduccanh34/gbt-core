# Installation

Getting started with GBT Core is simple! GBT is written in Python and can be installed easily using your favorite package manager.

## Prerequisites

- **Python 3.11+** or newer
- Access to your analytical source (e.g., **Trino**) and target Graph Database (e.g., **Neo4j**).

## Install GBT Core

To get started, you will need to install GBT and the specific adapter for your destination database. Currently, we natively support **Neo4j**.

### Option 1: Pip

Run the following command in your terminal to install GBT along with Neo4j destination dependencies:

```bash
pip install "gbt-core[neo4j]"
```

### Option 2: Poetry

If you are using [Poetry](https://python-poetry.org/) for your project's dependency management, you can add GBT by running:

```bash
poetry add "gbt-core[neo4j]"
```

## Verify Installation

After installation, verify that the CLI is working properly by invoking the help menu:

```bash
gbt --help
# Or if invoking directly from the module:
python -m core.gbt.cli.main --help
```
