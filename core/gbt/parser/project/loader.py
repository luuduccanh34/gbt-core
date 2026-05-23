from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from .model import GbtProjectConfig

class ProjectLoader:
    """
    A loader class responsible for resolving and parsing various configuration files
    within a given project directory (e.g., gbt_project.yaml, profiles.yaml).
    """

    def __init__(self, project_path: Optional[Path] = None, config_filename: str = "gbt_project.yaml") -> None:
        """
        Initialize the ConfigLoader.

        Args:
            project_path (Optional[Path]): The root directory of the project. Defaults to current working directory.
            config_filename (str): The name of the configuration file to load.
        """
        self.project_path = project_path or Path.cwd()
        self.config_filename = config_filename

    def load_raw_config(self) -> Dict[str, Any]:
        """
        Reads and parses the YAML configuration file based on the initialized parameters.

        Returns:
            Dict[str, Any]: A dictionary containing the parsed YAML data.

        Raises:
            FileNotFoundError: If the specified configuration file does not exist.
            yaml.YAMLError: If there is an error parsing the YAML file.
        """
        config_file = self.project_path / self.config_filename

        if not config_file.is_file():
            raise FileNotFoundError(f"Configuration file not found at: {config_file}")

        with config_file.open("r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        return config_data or {}

    def load_gbt_project_config(self) -> GbtProjectConfig:
        """
        Loads the configuration and maps it to a GbtProjectConfig model instance.

        Returns:
            GbtProjectConfig: The configuration model instance.
        """
        project_data = self.load_raw_config()
        return GbtProjectConfig(**project_data)
