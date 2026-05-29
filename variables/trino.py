"""
Trino Environment Variables Configuration
"""

from typing import Dict, Any
from variables.helper import BaseConfig

class TrinoVariables(BaseConfig):
    """
    Configuration mapped to Trino environment variables.

    This class defines the environment variable keys required for
    establishing a connection to the Trino database and provides a method
    to retrieve their values.

    Attributes:
        VARIABLES (list[str]): The required environment variable names for the Trino connection.

    Example:
        >>> from variables.trino import TrinoVariables
        >>> print(TrinoVariables.VARIABLES)
        ['TRINO_HOST', 'TRINO_PORT', 'TRINO_USER', 'TRINO_PASSWORD', 'TRINO_CATALOG', 'TRINO_SCHEMA']
    """

    VARIABLES = [
        "TRINO_HOST",
        "TRINO_PORT",
        "TRINO_USER",
        "TRINO_PASSWORD",
        "TRINO_CATALOG",
        "TRINO_SCHEMA"
    ]

    @classmethod
    def config(cls) -> Dict[str, Any]:
        """
        Retrieve the Trino configuration as a dictionary.

        Returns:
            Dict[str, Any]: A dictionary containing the configuration values
                            mapped from the Trino environment variables.

        Example:
            >>> from variables.trino import TrinoVariables
            >>> config_dict = TrinoVariables.config()
            >>> print(config_dict)
            {
                'TRINO_HOST': 'localhost',
                'TRINO_PORT': '8080',
                'TRINO_USER': 'trino',
                'TRINO_PASSWORD': 'password',
                'TRINO_CATALOG': 'hive',
                'TRINO_SCHEMA': 'default'
            }
        """
        return cls.load()
