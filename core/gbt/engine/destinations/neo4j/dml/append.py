from core.gbt.engine.base.destination import BaseCypherEngine
from typing import Any, Dict, Optional
from core.gbt.parser.manifest.loader import execute_load_manifest
from core.gbt.common.gbt import write_ddl_compile_cypher, load_manifest_config
from core.gbt.engine.sources.trino.adapter import TrinoSourceAdapter
from jinja2 import Environment, PackageLoader
from connectors.neo4j import Neo4jConnector
from core.gbt.validation.data_type.manager import ValidationManager
import logging

# Configure basic logging with colors for readability
logger = logging.getLogger(__name__)

class AppendEngine(BaseCypherEngine):
    """
    AppendEngine is responsible for appending data into Neo4j nodes.
    It reads raw data from a source (e.g., Trino), validates and cleans it
    using ValidationManager, and then executes Cypher DML queries to load
    the data into the target graph database.
    """
    def __init__(self, model_name: str, batch_size: int = 1000, connector: Optional[Neo4jConnector] = None):
        """
        Initializes the AppendEngine with model configuration and required connectors.

        Args:
            model_name (str): The name of the model being compiled and executed.
            batch_size (int): The number of rows to retrieve and process per batch.
            connector (Neo4jConnector, optional): Active Neo4j connector instance.
        """
        super().__init__()
        self.model_name = model_name
        self.batch_size = batch_size
        self.manifest = self._load_manifest()

        # Load the configuration specific to the provided model
        self.model_config = self.manifest.get(self.model_name, {})

        # Determine the model type ('node' or 'relationship')
        raw_models_config = self.model_config.get('models', {})
        try:
            self.type = raw_models_config.get('type', 'node').lower()
        except Exception as e:
            logger.error(f"Error extracting 'type' from model configuration for '{self.model_name}': {e}", exc_info=True)
            self.type = 'node'

        if self.type not in ['node', 'relationship']:
            logger.warning(f"Invalid 'type' specified in model '{self.model_name}': '{self.type}'. Defaulting to 'node'.")
            self.type = 'node'

        self.model_properties = raw_models_config.get('properties', [])

        # Default fallback for settings if any
        settings = raw_models_config.get('settings', {})
        self.on_schema_error = settings.get('on_schema_error', 'fail')

        # Connectors & Validators
        self.trino_adapter = TrinoSourceAdapter(model_name=self.model_name)
        self.neo4j_connector = connector if connector else Neo4jConnector()
        self.validator = ValidationManager(
            model_name=self.model_name,
            model_properties=self.model_properties,
            on_schema_error=self.on_schema_error
        )

    def _load_manifest(self) -> Dict[str, Any]:
        """
        Loads and returns the manifest configuration.
        """
        execute_load_manifest()
        return load_manifest_config()

    def compile(self) -> str:
        """
        Compiles the model configuration into a Cypher append DML statement.

        This method uses Jinja templates to render Cypher queries (e.g., MERGE/UNWIND)
        based on the extracted model's properties for both Nodes and Relationships. It writes
        the compiled statement to the target directory and returns the combined Cypher string.

        Returns:
            str: Compiled Cypher DML query for appending data.

        Raises:
            Exception: If an error occurs during rendering or writing the statements.
        """
        logger.info(f"Starting compilation for append DML query - model: {self.model_name} (Type: {self.type})")
        try:
            env = Environment(loader=PackageLoader(
                package_name='core.gbt',
                package_path='templates'
            ))

            raw_models_config = self.model_config.get('models', {})
            properties = self.model_properties

            if self.type == 'relationship':
                logger.debug(f"Compiling Append Cypher for Relationship: '{self.model_name}'")
                template = env.get_template('destinations/neo4j/dml/append_relation.cypher.j2')

                # Fetch relation-specific configs
                source_conf = raw_models_config.get('source_node', {})
                target_conf = raw_models_config.get('target_node', {})
                physical_name = raw_models_config.get('physical_name', raw_models_config.get('label', self.model_name))

                cypher_query = template.render(
                    source_label=source_conf.get('label'),
                    source_key=source_conf.get('key'),
                    source_ref=source_conf.get('ref'),
                    target_label=target_conf.get('label'),
                    target_key=target_conf.get('key'),
                    target_ref=target_conf.get('ref'),
                    physical_name=physical_name,
                    properties=properties
                )
            else:
                logger.debug(f"Compiling Append Cypher for Node: '{self.model_name}'")
                template = env.get_template('destinations/neo4j/dml/append_node.cypher.j2')

                node_label = raw_models_config.get('label', self.model_name)
                cypher_query = template.render(
                    node_label=node_label,
                    properties=properties
                )

            # Write compiled statement to file system
            write_ddl_compile_cypher(
                cypher_statements=cypher_query,
                model_path=self.model_name,
                ddl_cypher_path='cypher_dml',
                compile_model_name=f"{self.model_name}_append",
                file_type='cypher'
            )

            logger.info(f"\033[92mSuccessfully compiled append DML statement for model '{self.model_name}'.\033[0m")
            return cypher_query

        except Exception as e:
            logger.error(f"Error compiling append DML statement for model '{self.model_name}': {e}", exc_info=True)
            raise

    def execute(self) -> Any:
        """
        Executes the compiled DML query to append data.

        Reads batch data from the source adapter, validates it according to properties,
        and pushes it to Neo4j.

        Yields:
            int: The number of records successfully appended in the current batch.
        """
        logger.info(f"Starting execution for appending data - model: {self.model_name}")

        # 1. Compile the query if not passed
        cypher_append_query = self.compile()

        # 2. Extract data generator
        total_records = 0
        try:
            trino_data_generator = self.trino_adapter.execute(batch_size=self.batch_size)

            total_batches = 0
            for batch_index, batch in enumerate(trino_data_generator):
                # Clean and validate batch
                clean_batch = self.validator.process_batch(
                    batch_index=batch_index,
                    batch_data=batch
                )

                # Run query with cleaned batch parameter
                self.neo4j_connector.run_query(
                    query=cypher_append_query,
                    parameters={"batch_data": clean_batch}
                )
                total_batches += 1
                total_records += len(clean_batch)
                logger.debug(f"Successfully inserted batch {batch_index} into Neo4j.")
                yield len(clean_batch)

            logger.info(f"\033[92mExecution completed for model '{self.model_name}'. Total batches inserted: {total_batches}. Total records: {total_records}\033[0m")
        except Exception as e:
            logger.error(f"Error executing append for model '{self.model_name}': {e}", exc_info=True)
            raise


