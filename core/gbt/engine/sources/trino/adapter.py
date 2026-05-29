from connectors.trino.connector import TrinoConnector
from core.gbt.engine.base.source import BaseSourceConnectorEngine
from core.gbt.parser.manifest.loader import execute_load_manifest
from core.gbt.common.gbt import write_sql_compile_sources, load_manifest_config
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class TrinoSourceAdapter(BaseSourceConnectorEngine):
    """
    Trino source connector engine implementation for data retrieval operations.

    This engine is responsible for establishing connections to a Trino data source,
    compiling queries using Jinja templates (via manifest), and executing data retrieval operations
    based on the provided model definitions.
    """
    def __init__(self, model_name: str) -> None:
        """
        Initialize the TrinoSourceEngine for a specific model.

        Args:
            model_name (str): The name of the model to be processed by this engine.
        """
        super().__init__()
        self.model_name = model_name
        logger.debug(f"Initializing TrinoSourceEngine for model: '{self.model_name}'")
        self.manifest = self._load_manifest()
        self.trino_connector = TrinoConnector()
        logger.info(f"TrinoSourceEngine initialized successfully for model: '{self.model_name}'")

    def _load_manifest(self) -> Dict[str, Any]:
        """
        Load the project manifest configuration.

        Returns:
            Dict[str, Any]: The loaded manifest configuration dictionary.
        """
        logger.debug("Executing load manifest process...")
        execute_load_manifest()
        manifest = load_manifest_config()
        logger.debug("Manifest loaded successfully.")
        return manifest

    def connect(self) -> Any:
        """
        Establish a connection to the Trino data source.

        Returns:
            Any: The active Trino connection object.
        """
        logger.info("Connecting to Trino database...")
        return self.trino_connector.connect()

    def compile(self) -> Tuple[str, str]:
        """
        Compile the SQL query for the given model and write the compiled source to a file.

        Returns:
            Tuple[str, str]: A tuple containing the original SQL script and the explicit connector name.

        Raises:
            KeyError: If required configuration keys are missing in the manifest.
        """
        logger.info(f"Compiling SQL sources for model: '{self.model_name}'")
        try:
            model_config = self.manifest[self.model_name]
            connector_name = model_config['script']['connector']
            sql_query = model_config['script']['original_script']

            logger.debug(f"Writing compiled SQL source for model: '{self.model_name}' (Connector: {connector_name})")
            write_sql_compile_sources(
                sql_statements=sql_query,
                model_path=model_config['models']['label'],
                sql_sources_path=f'{connector_name}/sql_sources',
                compile_model_name=self.model_name
            )
            logger.info(f"Successfully compiled SQL sources for model: '{self.model_name}'")
            return sql_query, connector_name
        except KeyError as e:
            logger.error(f"Missing configuration key for model '{self.model_name}': {e}", exc_info=True)
            raise

    def execute(self, query: str = '', batch_size: int = 1000, **kwargs: Any) -> Any:
        """
        Execute a SQL query against Trino and yield the results in batches.

        If a query is not directly provided, it will compile and use the query from the model's manifest.

        Args:
            query (str, optional): The SQL query string to execute. Defaults to an empty string.
            batch_size (int, optional): Number of rows to fetch per yield. Defaults to 1000.
            **kwargs: Additional execution options.

        Returns:
            Any: Sequence of row batches fetched from the query.

        Raises:
            ValueError: If the connector specified in the model configuration is not 'trino'.
        """
        if not query:
            logger.debug("No direct query provided. Falling back to model's compiled query.")
            sql_query_compiled, connector_name = self.compile()

            if connector_name != 'trino':
                logger.error(f"Connector mismatch for model '{self.model_name}': expected 'trino', got '{connector_name}'")
                raise ValueError(f"Invalid connector specified in model configuration: expected 'trino', got '{connector_name}'")

            final_query = sql_query_compiled
        else:
            final_query = query

        logger.info(f"Executing query on Trino with batch_size={batch_size}")
        return self.trino_connector.execute_query(final_query, batch_size=batch_size, **kwargs)

    def count_total(self, query: str = '') -> int:
        """
        Count the total number of records that would be returned by the query.

        Args:
            query (str, optional): The SQL query string. If empty, compiles from manifest.

        Returns:
            int: The total count of records.
        """
        if not query:
            sql_query_compiled, connector_name = self.compile()
            if connector_name != 'trino':
                raise ValueError(f"Invalid connector specified in model configuration: expected 'trino', got '{connector_name}'")
            final_query = sql_query_compiled
        else:
            final_query = query

        count_query = f"SELECT count(*) as total_count FROM ({final_query}) AS temp_count"
        logger.info("Executing count query on Trino to determine total records.")
        # execute_query returns a generator, so we fetch the first batch and the first row
        results_gen = self.trino_connector.execute_query(count_query, batch_size=1)
        for batch in results_gen:
            if batch and len(batch) > 0:
                count_val = batch[0].get('total_count', batch[0].get('_col0', 0))
                return int(count_val)
        return 0
