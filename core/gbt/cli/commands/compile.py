# core/gbt/cli/commands/compile.py
import logging
import click

from core.gbt.engine.destinations.neo4j.ddl.schema_builder import SchemaBuilderEngine

logger = logging.getLogger(__name__)

def log_info(msg: str, bold: bool = False) -> None:
    """Prints a formatted informative message to the console with cyan color."""
    click.secho(f"🤖 [INFO] {msg}", fg="cyan", bold=bold)

def log_success(msg: str, bold: bool = True) -> None:
    """Prints a formatted success message to the console with green color."""
    click.secho(f"🎉 [SUCCESS] {msg}", fg="green", bold=bold)

def log_error(msg: str, bold: bool = True) -> None:
    """Prints a formatted error message to the console with red color."""
    click.secho(f"❌ [ERROR] {msg}", fg="red", bold=bold)

@click.command(name="run")
@click.option(
    "--select",
    required=True,
    type=str,
    help="Specify the exact literal Cypher model name to be executed."
)
@click.option(
    "--profiles-dir",
    default=".",
    type=str,
    help="Directory containing the profiles.yaml file (currently ignored in V1)."
)
@click.option(
    "--target",
    required=True,
    type=str,
    help="Target Graph Database name on Neo4j."
)
def compile(select: str, profiles_dir: str, target: str) -> None:
    """
    Execute DDL operations for a specific model against the target Graph Database.

    This command initializes the database connection and the schema builder engine,
    then executes the compiled Cypher statements sequentially.
    """
    logger.info(f"Starting 'run' command for model: {select} on target: {target}")

    engine = SchemaBuilderEngine(model_name=select)

    engine.compile()
