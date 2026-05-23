import logging
from typing import Optional, Any, Dict, List
from variables.neo4j import Neo4jVariables

try:
    from neo4j import GraphDatabase, Driver
except ImportError:
    GraphDatabase = None
    Driver = Any

logger = logging.getLogger(__name__)

class Neo4jConnector:
    """
    A unified connector for Neo4j supporting two main use cases:
    1. Standard connection (CRUD data on a specific database).
    2. Administrative connection (Creating users, databases, and fetching metadata via 'system' DB).
    """

    def __init__(self, uri: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None, database: Optional[str] = None) -> None:
        """
        Initialize the connector properties.

        Args:
            uri (str, optional): The connection URI. Falls back to NEO4J_URI environment variable if not provided.
            username (str, optional): The database username. Falls back to NEO4J_USERNAME environment variable.
            password (str, optional): The database password. Falls back to NEO4J_PASSWORD environment variable.
            database (str, optional): The default database name. Falls back to NEO4J_DATABASE environment variable or 'neo4j'.
        """
        neo4jConfig = Neo4jVariables.config()
        self._uri = uri or neo4jConfig.get("NEO4J_URI", "")
        self._username = username or neo4jConfig.get("NEO4J_USERNAME", "")
        self._password = password or neo4jConfig.get("NEO4J_PASSWORD", "")
        self._database = database or neo4jConfig.get("NEO4J_DATABASE", "neo4j")
        self._driver: Optional[Driver] = None
        self._is_http = self._uri.startswith("http")

    def connect(self) -> None:
        """
        Establish the connection to Neo4j. (Only supports Bolt/Neo4j protocol)
        """
        if self._is_http:
            raise ValueError("The connect() method only supports bolt/neo4j protocols, but an HTTP URI was provided.")

        if GraphDatabase is None:
            raise ImportError("neo4j driver is not installed. Please install it using 'pip install neo4j'.")

        if not self._driver:
            self._driver = GraphDatabase.driver(self._uri, auth=(self._username, self._password))
            logger.info("Successfully established connection to Neo4j at %s", self._uri)

    def close(self) -> None:
        """
        Close the underlying Neo4j driver connection.
        """
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Closed Neo4j connection.")

    # ----------------------------------------------------
    # DIRECTION 1: Normal Application Execution
    # ----------------------------------------------------
    def run_query(self, query: str, parameters: Optional[Dict[str, Any]] = None, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Run a normal application query against a target database.

        Args:
            query (str): The Cypher query to execute.
            parameters (dict, optional): Parameters for the query.
            database (str, optional): The target database. Defaults to the initialized database.

        Returns:
            List[Dict[str, Any]]: The list of records parsed as dicts.
        """
        target_db = database or self._database

        if self._is_http:
            return self._run_http_query(query, parameters, target_db)

        if not self._driver:
            self.connect()

        with self._driver.session(database=target_db) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def _run_http_query(self, query: str, parameters: Optional[Dict[str, Any]] = None, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Internal method to run cypher over Neo4j HTTP Transaction API.
        """
        import requests
        from requests.auth import HTTPBasicAuth

        base_uri = self._uri.rstrip("/")
        url = f"{base_uri}/db/{database}/tx/commit"
        payload = {
            "statements": [
                {
                    "statement": query,
                    "parameters": parameters or {}
                }
            ]
        }
        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth(self._username, self._password),
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        response.raise_for_status()
        data = response.json()

        if data.get("errors"):
            raise Exception(f"Neo4j HTTP Query Error: {data['errors']}")

        results = []
        for result in data.get("results", []):
            columns = result.get("columns", [])
            for datum in result.get("data", []):
                record = dict(zip(columns, datum.get("row", [])))
                results.append(record)
        return results

    # ----------------------------------------------------
    # DIRECTION 2: System / Administrative Execution
    # ----------------------------------------------------
    def run_admin_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Run an administrative query against the internal 'system' database.
        Useful for metadata fetching, or user/database management.

        Args:
            query (str): The Cypher admin query (e.g., SHOW DATABASES, CREATE USER, etc.).
            parameters (dict, optional): Parameters for the query.

        Returns:
            List[Dict]: Records representing admin information.
        """
        # Admin tasks in Neo4j must be executed on the 'system' database.
        return self.run_query(query, parameters, database="system")

    def show_databases(self) -> List[Dict[str, Any]]:
        """
        Utility method to fetch existing databases.
        """
        return self.run_admin_query("SHOW DATABASES YIELD name, currentStatus, role")

    def create_database(self, db_name: str) -> None:
        """
        Utility method to create a new database.
        """
        # In Cypher, identifiers like DB names generally cannot be parameterized directly with $param.
        # Ensure the db_name is safe and properly escaped if dynamically injected.
        self.run_admin_query(f"CREATE DATABASE {db_name} IF NOT EXISTS")
        logger.info("Executed database creation for: %s", db_name)
