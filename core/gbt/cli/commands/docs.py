import click
import subprocess
import os
from rich.console import Console

console = Console()

@click.command(name="docs")
@click.option("--port", default=3401, help="Port to serve the documentation on (default: 3401).")
def docs(port: int):
    """
    Generate and serve the GBT documentation locally.
    """
    console.print(f"[bold cyan]🚀 Starting GBT documentation server on http://localhost:{port}...[/bold cyan]")

    docs_dir = os.path.join(os.getcwd(), "docs")
    mkdocs_yml_path = os.path.join(os.getcwd(), "mkdocs.yml")

    if not os.path.exists(docs_dir) or not os.path.exists(mkdocs_yml_path):
        console.print("[yellow]mkdocs format not fully initialized. Generating templates...[/yellow]")
        _init_docs_structure(docs_dir)
        _create_mkdocs_yml(mkdocs_yml_path)
        console.print("[green]Created basic documentation structure![/green]")

    try:
        subprocess.run(["mkdocs", "serve", "-a", f"localhost:{port}"], check=True)
    except FileNotFoundError:
        console.print("[bold red]❌ mkdocs is not installed. Please install mkdocs-material:[/bold red]")
        console.print("   pip install mkdocs-material")
        raise click.Abort()
    except Exception as e:
        console.print(f"[bold red]❌ Failed to start docs server: {e}[/bold red]")
        raise click.Abort()

def _init_docs_structure(docs_dir: str):
    """Creates a basic documentation template structure."""
    os.makedirs(docs_dir, exist_ok=True)

    structure = {
        "index.md": "# Welcome to GBT Core\n\nGraph Build Tool (GBT) documentation.",
        "getting-started/installation.md": "# Installation\n\nInstructions to install GBT.",
        "getting-started/quickstart.md": "# Quickstart\n\nRun your first project.",
        "architecture/core-engine.md": "# Core Engine\n\nDetails on how the Engine works.",
        "architecture/parser.md": "# Parser\n\nDetails on the Manifest load and script parsers.",
        "architecture/templates.md": "# Templates\n\nJinja templates reference.",
    }

    for path, content in structure.items():
        file_path = os.path.join(docs_dir, path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

def _create_mkdocs_yml(mkdocs_yml_path: str):
    """Creates the root mkdocs.yml configuration."""
    yaml_config = '''site_name: GBT Core Documentation
site_description: Enterprise Graph Build Tool documentation
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.top
    - toc.integrate
    - search.suggest
    - search.highlight
    - content.code.copy
nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quickstart: getting-started/quickstart.md
  - Architecture:
    - Core Engine: architecture/core-engine.md
    - Parser: architecture/parser.md
    - Templates: architecture/templates.md
  - Publishing: publish-to-pypi.md
'''
    if not os.path.exists(mkdocs_yml_path):
        with open(mkdocs_yml_path, "w", encoding="utf-8") as f:
            f.write(yaml_config)
