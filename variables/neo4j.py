"""
Neo4j Environment Variables Configuration
"""

from typing import Dict, Any
from variables.helper import BaseConfig

class Neo4jVariables(BaseConfig):
    """
    Configuration mapped to Neo4j environment variables.

    This class defines the environment variable keys required for
    establishing a connection to the Neo4j database and provides a method
    to retrieve their values.

    Attributes:
        VARIABLES (list[str]): The required environment variable names for the Neo4j connection.

    Example:
        >>> from variables.neo4j import Neo4jVariables
        >>> print(Neo4jVariables.VARIABLES)
        ['NEO4J_URI', 'NEO4J_USERNAME', 'NEO4J_PASSWORD', 'NEO4J_DATABASE']
    """

    VARIABLES = [
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "NEO4J_DATABASE"
    ]

    @classmethod
    def config(cls) -> Dict[str, Any]:
        """
        Retrieve the Neo4j configuration as a dictionary.

        Args:
            None (Takes no explicit arguments, uses class method context).

        Returns:
            Dict[str, Any]: A dictionary containing the configuration values
                            mapped from the Neo4j environment variables.

        Example:
            >>> from variables.neo4j import Neo4jVariables
            >>> config_dict = Neo4jVariables.config()
            >>> print(config_dict)
            {
                'NEO4J_URI': 'bolt://localhost:7687',
                'NEO4J_USERNAME': 'neo4j',
                'NEO4J_PASSWORD': 'password',
                'NEO4J_DATABASE': 'neo4j'
            }
        """
        return cls.load()
