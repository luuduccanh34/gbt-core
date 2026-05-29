import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .file import FileHandler
from ..parser.project.loader import ProjectLoader
from ..parser.project.model import GbtProjectConfig

logger = logging.getLogger(__name__)


def load_project_config(project_path: Optional[Path] = None) -> GbtProjectConfig:
    """
    Convenience function to load and parse the default GBT project configuration file.

    Args:
        project_path (Optional[Path]): The root directory of the project. Defaults to current working directory.

    Returns:
        GbtProjectConfig: The loaded and parsed project configuration object.
    """
    logger.debug(f"Loading project config from {project_path or 'current directory'}")
    loader = ProjectLoader(project_path=project_path, config_filename="gbt_project.yaml")
    return loader.load_gbt_project_config()

def load_profiles_config(project_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Convenience function to load and parse the profiles configuration file.

    Args:
        project_path (Optional[Path]): The root directory of the project. Defaults to current working directory.

    Returns:
        Dict[str, Any]: The loaded profiles configuration dictionary.
    """
    logger.debug(f"Loading profiles config from {project_path or 'current directory'}")
    loader = ProjectLoader(project_path=project_path, config_filename="profiles.yaml")
    return loader.load_raw_config()

def load_target_path(project_path: Optional[Path] = None) -> str:
    """
    Retrieves the target path from the project configuration.

    Args:
        project_path (Optional[Path]): The root directory of the project. Defaults to current working directory.

    Returns:
        str: The configured target path for compiled artifacts.

    Raises:
        ValueError: If 'target_path' is not defined in the project configuration.
    """
    project_config = load_project_config(project_path=project_path)
    if not getattr(project_config, "target_path", None):
        error_msg = "The 'target_path' is not defined in the project configuration."
        logger.error(error_msg)
        raise ValueError(error_msg)
    return project_config.target_path

def load_models_paths(project_path: Optional[Path] = None) -> list:
    """
    Retrieves the list of model paths from the project configuration.

    Args:
        project_path (Optional[Path]): The root directory of the project. Defaults to current working directory.

    Returns:
        list: A list of paths where data models are stored.

    Raises:
        ValueError: If 'model_paths' is not defined in the project configuration.
    """
    project_config = load_project_config(project_path=project_path)
    if not getattr(project_config, "model_paths", None):
        error_msg = "The 'model_paths' is not defined in the project configuration."
        logger.error(error_msg)
        raise ValueError(error_msg)
    return project_config.model_paths

def load_manifest_config(manifest_path: str = "manifest/manifest.json") -> Dict[str, Any]:
    """
    Loads the manifest configuration file into a dictionary.

    This function retrieves the project's target directory from the project
    configuration, constructs the full path to the manifest JSON file, and
    safely attempts to read its contents.

    Args:
        manifest_path (str): The relative path to the manifest file inside the
            target directory (default is "manifest/manifest.json").

    Returns:
        Dict[str, Any]: The parsed JSON data from the manifest.

    Raises:
        ValueError: If 'target_path' is missing from the project configuration.
        FileNotFoundError: If the manifest file cannot be found.
        Exception: For any other unexpected errors during the loading process.
    """
    logger.info(f"Attempting to load manifest from relative path: '{manifest_path}'")

    try:
        gbt_project_loader = ProjectLoader()
        gbt_project_config = gbt_project_loader.load_gbt_project_config()
    except Exception as e:
        logger.error(f"Failed to load project configuration: {e}")
        raise

    if not getattr(gbt_project_config, "target_path", None):
        error_msg = "The 'target_path' is not defined in the project configuration."
        logger.error(error_msg)
        raise ValueError(error_msg)

    target_file_path = Path.cwd() / gbt_project_config.target_path
    manifest_file_path = target_file_path / manifest_path

    logger.debug(f"Resolved manifest file path to: {manifest_file_path}")

    if not manifest_file_path.exists():
        error_msg = f"Manifest file not found at '{manifest_file_path.resolve()}'"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        # Use FileHandler statically as refactored previously
        manifest_data = FileHandler.read_file(
            file_path=manifest_file_path,
            file_type="json"
        )
        logger.info(f"Successfully loaded manifest from '{manifest_file_path}'")
        return manifest_data
    except Exception as e:
        logger.error(f"Failed to read manifest file: {e}")
        raise

def write_ddl_compile_cypher(
    cypher_statements: str,
    model_path: str,
    compile_model_name: str,
    ddl_cypher_path: str = 'cypher_ddl',
    compile_path: str = 'compile',
    file_type: str = 'cypher'
) -> None:
    """
    Writes compiled Cypher statements to the designated target directory.

    Args:
        cypher_statements (str): The Cypher queries to write.
        model_path (str): The directory path for the model.
        compile_model_name (str): The base name for the output file.
        ddl_cypher_path (str, optional): Target sub-directory for DDL files. Defaults to 'cypher_ddl'.
        compile_path (str, optional): Base directory name for compiled files. Defaults to 'compile'.
        file_type (str, optional): The extension of the output file. Defaults to 'cypher'.
    """
    try:
        root_dir = Path.cwd()
        gbt_project_config = load_project_config()

        # Determine target path from config
        target_dir = root_dir / gbt_project_config.target_path

        # Build the final output path
        output_file = target_dir / compile_path / model_path / ddl_cypher_path / f"{compile_model_name}.{file_type}"

        logger.info(f"Writing compiled Cypher statements to: {output_file}")

        # Write statements to file using FileHandler
        FileHandler.write_file(
            file_path=output_file,
            data=cypher_statements,
            file_type=file_type
        )

        logger.info(f"Successfully wrote Cypher statements to: {output_file}")
    except Exception as e:
        logger.error(f"Failed to write Cypher statements: {e}")
        raise

def write_sql_compile_sources(
    sql_statements: str,
    model_path: str,
    compile_model_name: str,
    sql_sources_path: str = 'sql_sources',
    compile_path: str = 'compile',
    file_type: str = 'sql'
) -> None:
    """
    Writes compiled SQL statements to the designated target directory.

    Args:
        sql_statements (str): The SQL queries to write.
        model_path (str): The directory path for the model.
        compile_model_name (str): The base name for the output file.
        sql_sources_path (str, optional): Target sub-directory for SQL sources. Defaults to 'sql_sources'.
        compile_path (str, optional): Base directory name for compiled files. Defaults to 'compile'.
        file_type (str, optional): The extension of the output file. Defaults to 'sql'.
    """
    try:
        root_dir = Path.cwd()
        gbt_project_config = load_project_config()

        # Determine target path from config
        target_dir = root_dir / gbt_project_config.target_path

        # Build the final output path
        output_file = target_dir / compile_path / model_path / sql_sources_path / f"{compile_model_name}.{file_type}"

        logger.info(f"Writing compiled SQL statements to: {output_file}")

        # Write statements to file using FileHandler
        FileHandler.write_file(
            file_path=output_file,
            data=sql_statements,
            file_type=file_type
        )

        logger.info(f"Successfully wrote SQL statements to: {output_file}")
    except Exception as e:
        logger.error(f"Failed to write SQL statements: {e}")
        raise