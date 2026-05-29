import yaml
import json
import logging
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

class FileHandler:
    """
    A utility class for handling standard file operations.
    Provides static methods to cleanly read from and write to various file formats.
    Currently supports reading 'yaml' and 'json', and writing 'yaml', 'json', 'cypher', 'txt', and 'sql'.
    """

    @staticmethod
    def read_file(file_path: Path, file_type: str) -> Any:
        """
        Reads and parses data from a file based on the specified format.

        Args:
            file_path (Path): The absolute or relative path to the file to be read.
            file_type (str): The format of the file (e.g., 'yaml', 'json').

        Returns:
            Any: The parsed data structure (typically a dict or list) loaded from the file.

        Raises:
            ValueError: If the requested file_type is not supported.
            FileNotFoundError: If the specified file_path does not exist.
            json.JSONDecodeError: If a JSON file contains invalid formatting.
            yaml.YAMLError: If a YAML file contains invalid formatting.
        """
        logger.info(f"Reading file: {file_path} with type: {file_type}")
        file_type = file_type.lower()
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            if file_type == "yaml":
                with file_path.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    logger.debug(f"Successfully loaded yaml data from {file_path}")
                    return data
            elif file_type == "json":
                with file_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.debug(f"Successfully loaded json data from {file_path}")
                    return data
            else:
                logger.error(f"Unsupported file type: '{file_type}'")
                raise ValueError(f"Unsupported file type: '{file_type}'. Supported types are 'yaml' and 'json'.")
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

    @staticmethod
    def write_file(file_path: Path, data: Any, file_type: str) -> None:
        """
        Serializes and writes data to a file in the specified format.

        Args:
            file_path (Path): The target path where the data should be saved.
            data (Any): The data payload to be serialized and written to the file.
            file_type (str): The target format for serialization (e.g., 'yaml', 'json', 'cypher', 'txt', 'sql').

        Raises:
            ValueError: If the requested file_type is not supported.
            IOError: If permissions or disk issues prevent writing to the file.
            Exception: For any other unexpected errors during writing.
        """
        logger.info(f"Writing data to file: {file_path} with type: {file_type}")
        file_type = file_type.lower()

        # Ensure parent directories exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if file_type == "yaml":
                with file_path.open("w", encoding="utf-8") as f:
                    yaml.safe_dump(data, f)
                    logger.debug(f"Successfully wrote yaml data to {file_path}")
            elif file_type == "json":
                with file_path.open("w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                    logger.debug(f"Successfully wrote json data to {file_path}")
            elif file_type == "cypher":
                with file_path.open("w", encoding="utf-8") as f:
                    # Expecting data to be a string representing cypher query
                    f.write(str(data))
                    logger.debug(f"Successfully wrote cypher data to {file_path}")
            elif file_type == "txt":
                with file_path.open("w", encoding="utf-8") as f:
                    # Expecting data to be a string representing text content
                    f.write(str(data))
                    logger.debug(f"Successfully wrote text data to {file_path}")
            elif file_type == "sql":
                with file_path.open("w", encoding="utf-8") as f:
                    # Expecting data to be a string representing SQL query
                    f.write(str(data))
                    logger.debug(f"Successfully wrote sql data to {file_path}")
            else:
                logger.error(f"Unsupported file type: '{file_type}'")
                raise ValueError(f"Unsupported file type: '{file_type}'. Supported types are 'yaml', 'json', 'cypher', 'txt', and 'sql'.")
        except Exception as e:
            logger.error(f"Error writing to file {file_path}: {e}")
            raise
