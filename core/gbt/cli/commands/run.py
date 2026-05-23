# core/gbt/cli/commands/run.py
import logging
import click

from core.gbt.engine.ddl.schema_builder import SchemaBuilderEngine
from connectors.neo4j import Neo4jConnector

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
def run(select: str, profiles_dir: str, target: str) -> None:
    """
    Execute DDL operations for a specific model against the target Graph Database.

    This command initializes the database connection and the schema builder engine,
    then executes the compiled Cypher statements sequentially.
    """
    logger.info(f"Starting 'run' command for model: {select} on target: {target}")

    # 1. Initialize Database Connector
    # Credentials (URI, user, pass) are expected to be auto-loaded via environment variables.
    try:
        log_info(f"Initializing Neo4jConnector for target database: '{target}'...")
        neo4j_connector = Neo4jConnector(database=target)
    except Exception as e:
        log_error(f"Failed to initialize Neo4j connection: {e}")
        logger.exception("Neo4jConnector initialization failed.")
        raise click.ClickException(f"Connection Initialization Error: {e}")

    # 2. Initialize Engine and Execute DDL commands
    try:
        log_info(f"Initializing SchemaBuilderEngine for model: '{select}'...")
        engine = SchemaBuilderEngine(model_name=select)

        log_info(f"Executing DDL statements on Neo4j (Database: '{target}')...", bold=True)
        engine.execute(connector=neo4j_connector)

        log_success(f"Successfully applied schema structure for model: '{select}'!")
        logger.info(f"Execution completed successfully for model '{select}'.")

    except Exception as e:
        log_error(f"Execution failed for model '{select}': {e}")
        logger.exception(f"Execution failed for model '{select}'.")
        raise click.ClickException(f"Execution Failed: {e}")
