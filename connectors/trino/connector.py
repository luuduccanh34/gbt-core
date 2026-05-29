import logging
from typing import Any, List, Iterator, Optional
import trino
from trino.auth import BasicAuthentication
import urllib3
from connectors.base import BaseConnector
from variables.trino import TrinoVariables

logger = logging.getLogger(__name__)

# Suppress insecure request warnings for unverified HTTPS connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TrinoConnector(BaseConnector):
    """
    A professional Trino connector for establishing connections, executing queries,
    and managing database interactions with built-in logging and error handling.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
        verify: bool = False,
        http_scheme: str = 'https',
        **kwargs: Any
    ) -> None:
        """
        Initialize the TrinoConnector.

        Args:
            host (str, optional): The Trino server hostname. Falls back to TRINO_HOST env var.
            port (int, optional): The Trino server port. Falls back to TRINO_PORT env var.
            user (str, optional): The username for connection. Falls back to TRINO_USER env var.
            password (str, optional): The password for the user. Falls back to TRINO_PASSWORD env var.
            catalog (str, optional): The specific catalog to connect to. Falls back to TRINO_CATALOG env var.
            schema (str, optional): The schema to use. Falls back to TRINO_SCHEMA env var or 'default'.
            verify (bool): Whether to verify SSL certificates (default: False).
            http_scheme (str): The HTTP scheme to use, e.g., 'http' or 'https' (default: 'https').
            **kwargs: Additional parameters to pass to the Trino connection.
        """
        trino_config = TrinoVariables.config()
        self.host = host or trino_config.get("TRINO_HOST", "")

        env_port = trino_config.get("TRINO_PORT")
        if port is not None:
            self.port = port
        elif env_port:
            self.port = int(env_port)
        else:
            self.port = 8080

        self.user = user or trino_config.get("TRINO_USER", "")
        self.password = password or trino_config.get("TRINO_PASSWORD", "")
        self.catalog = catalog or trino_config.get("TRINO_CATALOG", "rest")
        self.schema = schema or trino_config.get("TRINO_SCHEMA", "default")

        self.verify = verify
        self.http_scheme = http_scheme
        self.extra_params = kwargs
        self._conn: Optional[trino.dbapi.Connection] = None

        logger.debug(
            f"Initialized TrinoConnector for user '{self.user}' at "
            f"'{self.host}:{self.port}' (catalog: '{self.catalog}', schema: '{self.schema}')"
        )

    def __enter__(self) -> 'TrinoConnector':
        """Allows use of the connector as a context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Ensures the connection is closed when exiting the context manager."""
        self.close()

    def connect(self) -> trino.dbapi.Connection:
        """
        Establish a connection to the Trino database.

        Returns:
            trino.dbapi.Connection: The active Trino connection object.

        Raises:
            trino.exceptions.TrinoQueryError: If the connection to Trino fails.
            Exception: For other unexpected failures.
        """
        if self._conn is None:
            logger.info(f"Establishing connection to Trino at {self.host}:{self.port}...")
            try:
                self._conn = trino.dbapi.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    catalog=self.catalog,
                    http_scheme=self.http_scheme,
                    auth=BasicAuthentication(self.user, self.password),
                    schema=self.schema,
                    verify=self.verify,
                    **self.extra_params
                )
                logger.info("Successfully connected to Trino.")
            except Exception as e:
                logger.error(f"Failed to connect to Trino: {e}", exc_info=True)
                raise
        else:
            logger.debug("Using existing Trino connection.")

        return self._conn

    def close(self) -> None:
        """
        Close the active Trino database connection safely.
        """
        if self._conn is not None:
            try:
                logger.info("Closing Trino connection...")
                self._conn.close()
                logger.info("Trino connection closed successfully.")
            except Exception as e:
                logger.warning(f"Error while closing Trino connection: {e}", exc_info=True)
            finally:
                self._conn = None
        else:
            logger.debug("Trino connection is already closed or was never opened.")

    def execute_query(self, query: str, **kwargs: Any) -> Iterator[List[Any]]:
        """
        Execute a SQL query against Trino and yield the results as lists of dictionaries in batches.

        This method handles connecting, acquiring a cursor, executing the query, mapping
        column names to row values, and yielding batches of dictionaries.

        Args:
            query (str): The SQL query string to execute.
            **kwargs: Additional execution options:
                - batch_size (int): Number of rows to fetch per yield (default: 1000).

        Yields:
            Iterator[List[dict]]: Sequence of row batches fetched from the query, where each row
            is represented as a dictionary mapping column names to their respective values.

        Raises:
            Exception: If query execution, cursor acquisition, or fetching fails.
        """
        batch_size = kwargs.get('batch_size', 1000)

        logger.debug(f"Executing query with batch_size={batch_size}:\n{query}")

        try:
            conn = self.connect()
            cursor = conn.cursor()
        except Exception as e:
            logger.error("Failed to acquire cursor for executing query.", exc_info=True)
            raise

        try:
            logger.info("Submitting query to Trino...")
            cursor.execute(query)
            logger.debug("Query successfully submitted. Mapping column names and fetching results...")

            # Extract column names from the cursor description
            column_names = [desc[0] for desc in cursor.description]
            logger.debug(f"Query returned columns: {column_names}")

            while True:
                batch = cursor.fetchmany(batch_size)
                if not batch:
                    logger.debug("All results fetched successfully.")
                    break

                logger.debug(f"Fetched {len(batch)} rows from Trino.")

                # Yield rows mapped with column names
                batch_dicts = [dict(zip(column_names, row)) for row in batch]
                yield batch_dicts

        except Exception as e:
            logger.error(f"Error executing query or fetching results: {e}", exc_info=True)
            raise
        finally:
            logger.debug("Closing query cursor.")
            try:
                cursor.close()
            except Exception as e:
                logger.warning(f"Failed to close cursor properly: {e}")
