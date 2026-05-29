# core/gbt/cli/commands/run.py
import logging
import time
import os
import psutil
import click
from rich.console import Console, Theme
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, MofNCompleteColumn

from core.gbt.engine.destinations.neo4j.ddl.schema_builder import SchemaBuilderEngine
from core.gbt.engine.destinations.neo4j.dml.append import AppendEngine
from core.gbt.engine.destinations.neo4j.dml.delete import DeleteEngine
from core.gbt.engine.destinations.neo4j.meta.inspector import InspectorEngine
from core.gbt.parser.manifest.loader import execute_load_manifest
from core.gbt.common.gbt import load_manifest_config
from connectors.neo4j import Neo4jConnector

logger = logging.getLogger(__name__)

# Define custom Rich Theme
custom_theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "error": "bold red",
    "step": "magenta",
    "warning": "yellow",
})

console = Console(theme=custom_theme)

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
@click.option(
    "--full-refresh",
    is_flag=True,
    default=False,
    help="If set, performs a full refresh by deleting existing schema elements before applying new ones."
)
def run(select: str, profiles_dir: str, target: str, full_refresh: bool) -> None:
    """
    Execute DML and DDL operations for a specific model against the target database.

    Args:
        select (str): The configured model name to run.
        profiles_dir (str): The path to the profiles directory.
        target (str): The target database identifier from profiles.
        full_refresh (bool): If True, clear existing data and constraints before running.
    """
    mode_str = "--full-refresh" if full_refresh else "default"

    # Detail steps for better execution plan panel
    if full_refresh:
        flow_steps = (
            "1. [cyan]Initialize[/cyan] (Connect DB)\n"
            "            2. [cyan]Manifest[/cyan]   (Load and extract configs)\n"
            "            3. [cyan]Cleanup[/cyan]    (Drop constraints & existing records)\n"
            "            4. [cyan]Schema[/cyan]     (Rebuild constraints & indexes)\n"
            "            5. [cyan]Append[/cyan]     (Stream and load records into Neo4j)"
        )
    else:
        flow_steps = (
            "1. [cyan]Initialize[/cyan] (Connect DB)\n"
            "            2. [cyan]Manifest[/cyan]   (Load and extract configs)\n"
            "            3. [cyan]Schema[/cyan]     (Create constraints & indexes if missing)\n"
            "            4. [cyan]Append[/cyan]     (Stream and load records into Neo4j)"
        )

    logger.info(f"Starting 'run' command for model: {select} on target: {target} with mode: {mode_str}")

    # Pre-execution plan
    plan_text = (
        f"[bold]{'Model:':<11}[/bold] {select}\n"
        f"[bold]{'Target DB:':<11}[/bold] {target}\n"
        f"[bold]{'Mode:':<11}[/bold] {mode_str}\n"
        f"[bold]{'Steps:':<11}[/bold] {flow_steps}"
    )

    console.print(Panel(plan_text, title="🚀 GBT PIPELINE EXECUTION PLAN", border_style="cyan", expand=False))
    console.print()

    global_start_time = time.time()
    process = psutil.Process(os.getpid())
    process.cpu_percent() # Initialize CPU tracking

    # 1. Initialize Database Connector
    step1_start = time.time()
    console.print("[info]🔄 [Step 1] Initializing Neo4j Database Connection...[/info]")
    try:
        with console.status("[info]Connecting to database...[/info]", spinner="dots"):
            neo4j_connector = Neo4jConnector(database=target)
            # Fetch Neo4j connection details
            conn_uri = neo4j_connector._uri
            conn_user = neo4j_connector._username
            conn_db = neo4j_connector._database

        elapsed_step1 = time.time() - step1_start
        console.print(f"[success]✔️  [Step 1] Connected to Neo4j successfully. ({elapsed_step1:.2f}s)[/success]")
        console.print(f"   [dim]{'URI:':<19} {conn_uri}[/dim]")
        console.print(f"   [dim]{'User:':<19} {conn_user}[/dim]")
        console.print(f"   [dim]{'Database:':<19} {conn_db}[/dim]")
        console.print()
    except Exception as e:
        console.print(f"[error]❌ [Step 1] Failed to initialize Neo4j connection: {e}[/error]")
        logger.exception("Neo4jConnector initialization failed.")
        raise click.ClickException(f"Connection Initialization Error: {e}")

    # 2. Execution Phase
    total_records_processed = 0
    try:
        # Step 2: Load Manifest
        step2_start = time.time()
        console.print("[info]🔄 [Step 2] Loading manifest configuration...[/info]")
        with console.status("[info]Parsing manifest file...[/info]", spinner="dots"):
            execute_load_manifest()
            manifest = load_manifest_config()

            model_config = manifest.get(select)
            if not model_config:
                raise click.ClickException(f"Model '{select}' not found in manifest file.")

            # Look up model info from the nested 'models' key
            manifest_models_block = model_config.get('models', {})
            # Determine the object type (e.g., 'node', 'label', 'relationship')
            object_type = manifest_models_block.get('type', 'node')
            model_label = manifest_models_block.get('label', select)

            # Fetch settings
            model_settings = manifest_models_block.get('settings', {})
            contract_enforced = model_settings.get('contract', {}).get('enforced', False)
            on_schema_error = model_settings.get('on_schema_error', 'fail')

            # Additional Relationship configurations
            physical_name = manifest_models_block.get('physical_name', select)
            source_node = manifest_models_block.get('source_node', {})
            target_node = manifest_models_block.get('target_node', {})

            total_models = len(manifest)

        elapsed_step2 = time.time() - step2_start
        console.print(f"[success]✔️  [Step 2] Manifest loaded! Located config for '{select}' among {total_models} parsed models. ({elapsed_step2:.2f}s)[/success]")
        console.print(f"   [dim]{'Model Name:':<19} {select}[/dim]")
        console.print(f"   [dim]{'Label/Name:':<19} {model_label}[/dim]")

        if object_type == "relationship":
            console.print(f"   [dim]{'Physical Rel Name:':<19} {physical_name}[/dim]")
            console.print(f"   [dim]{'Source Node:':<19} {source_node.get('label')} (Key: {source_node.get('key')} -> Ref: {source_node.get('ref')})[/dim]")
            console.print(f"   [dim]{'Target Node:':<19} {target_node.get('label')} (Key: {target_node.get('key')} -> Ref: {target_node.get('ref')})[/dim]")

        console.print(f"   [dim]{'Object Type:':<19} {object_type}[/dim]")
        console.print(f"   [dim]{'Contract Enforced:':<19} {contract_enforced}[/dim]")
        console.print(f"   [dim]{'On Schema Error:':<19} {on_schema_error}[/dim]")
        console.print()

        current_step = 3

        # Step 3 (Optional): Full Refresh - Clean up Phase
        if full_refresh:
            step_cleanup_start = time.time()
            console.print(f"[step]🔄 [Step {current_step}] Full Refresh Cleanup Initiated...[/step]")

            with console.status(f"[step]Dropping constraints and data for '{select}'...[/step]", spinner="dots"):
                inspector_engine = InspectorEngine(
                    model_name=select,
                    object_type=object_type,
                    connector=neo4j_connector
                )
                constraints = inspector_engine.execute()
                if constraints:
                    for constraint in constraints:
                        constraint_name = constraint.get('name')
                        console.print(f"   [yellow]- Dropped constraint:[/yellow] '{constraint_name}'")
                        delete_engine_constraint = DeleteEngine(
                            model_name=select,
                            object_type='constraint',
                            connector=neo4j_connector
                        )
                        delete_engine_constraint.execute(constraint_name=constraint_name)
                else:
                    console.print("   [dim]- No existing constraints found to drop.[/dim]")

                # Step 2.2: Delete Graph Objects (Nodes/Labels/Relationships)
                if object_type in ['node', 'label', 'relationship']:
                    delete_engine_object = DeleteEngine(
                        model_name=select,
                        object_type=object_type,
                        connector=neo4j_connector
                    )
                    delete_engine_object.execute()
                    console.print(f"   [yellow]- Dropped {object_type} for '{select}' successfully on Neo4j.[/yellow]")

            elapsed_cleanup = time.time() - step_cleanup_start
            console.print(f"[success]✔️  [Step {current_step}] Cleanup finished successfully. ({elapsed_cleanup:.2f}s)[/success]")
            current_step += 1
            console.print()

        # Step 3/4: Schema Building Phase (Constraints & Indexes)
        step_schema_start = time.time()
        console.print(f"[info]🔄 [Step {current_step}] Compiling and building schema for '{select}'...[/info]")
        with console.status(f"[info]Applying schema to database...[/info]", spinner="dots"):
            schema_builder_engine = SchemaBuilderEngine(model_name=select)
            created_schemas = schema_builder_engine.execute(connector=neo4j_connector)
            if created_schemas:
                for schema in created_schemas:
                    schema_type = schema.get("type", "schema")
                    schema_name = schema.get("name", "unknown")
                    console.print(f"   [yellow]- Created {schema_type}:[/yellow] '{schema_name}'")
            else:
                console.print("   [dim]- No schemas require creation.[/dim]")

        elapsed_schema = time.time() - step_schema_start
        console.print(f"[success]✔️  [Step {current_step}] Schema elements and constraints applied to database. ({elapsed_schema:.2f}s)[/success]")
        current_step += 1
        console.print()

        # Step 4/5: Data Insertion Phase
        step_append_start = time.time()
        console.print(f"[warning]🔄 [Step {current_step}] Streaming and appending batch data for '{select}'...[/warning]")

        append_engine = AppendEngine(
            model_name=select,
            batch_size=1000,
            connector=neo4j_connector
        )

        with console.status("[warning]Calculating total records to stream...[/warning]", spinner="dots"):
            total_expected_records = append_engine.trino_adapter.count_total()

        total_records_processed = 0

        if total_expected_records > 0:
            console.print(f"   [dim]Target Type:      {object_type}[/dim]")
            console.print(f"   [dim]Batch Size:       {append_engine.batch_size}[/dim]")
            console.print(f"   [dim]Total Data Count: {total_expected_records} records[/dim]\n")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                "•",
                MofNCompleteColumn(),
                "•",
                TimeElapsedColumn(),
                console=console
            ) as progress:
                desc = f"[warning]Streaming '{object_type}' into Neo4j...[/warning]"
                task = progress.add_task(desc, total=total_expected_records)

                for batch_records_count in append_engine.execute():
                    total_records_processed += batch_records_count
                    progress.update(task, advance=batch_records_count)
        else:
            console.print("   [dim]- No records found to append in the source database.[/dim]")

        elapsed_append = time.time() - step_append_start
        console.print(f"[success]✔️  [Step {current_step}] Data append process completed. {total_records_processed} records inserted. ({elapsed_append:.2f}s)[/success]")

        # Completion Summary Panel
        global_elapsed = time.time() - global_start_time
        ram_usage = process.memory_info().rss / (1024 * 1024)
        cpu_usage = process.cpu_percent()

        console.print()

        summary_text = (
            f"Pipeline execution completed successfully!\n\n"
            f"📊 [bold]Total Records Inserted:[/bold] {total_records_processed}\n"
            f"⏱️  [bold]Total Execution Time:[/bold]   {global_elapsed:.2f} seconds\n"
            f"💻 [bold]Peak CPU Usage:[/bold]         {cpu_usage:.1f}%\n"
            f"🧠 [bold]Memory/RAM Consumed:[/bold]    {ram_usage:.1f} MB"
        )
        console.print(Panel(summary_text, title="✅ SUCCESS", border_style="green", expand=False))

    except Exception as e:
        console.print(f"\n[error]❌ Error during command execution: {e}[/error]")
        logger.error(f"Run command failed: {e}", exc_info=True)
        raise click.ClickException(str(e))
