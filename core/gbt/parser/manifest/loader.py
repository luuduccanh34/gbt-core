import json
import logging
import yaml
from pathlib import Path
from typing import Dict

from .model import ModelConfig
from ..project.loader import ProjectLoader, GbtProjectConfig

logger = logging.getLogger(__name__)
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

class ManifestLoader:
    """
    A class to handle the loading and saving of the GBT manifest.

    The manifest aggregates all model configurations present in the project's model directories.
    """

    def __init__(self, project_config: GbtProjectConfig):
        """
        Initializes the ManifestLoader.

        Args:
            project_config (GbtProjectConfig): The configuration of the current project.
        """
        self.project_config = project_config

    def load(self) -> Dict[str, ModelConfig]:
        """
        Scans the project model directories for YAML configuration files and constructs a manifest.

        Returns:
            Dict[str, ModelConfig]: A dictionary mapping the model name to its ModelConfig object.
        """
        manifest: Dict[str, ModelConfig] = {}

        if not hasattr(self.project_config, 'model_paths') or not self.project_config.model_paths:
            logger.warning("No model_paths defined in the project configuration.")
            return manifest

        for path_str in self.project_config.model_paths:
            model_dir = Path(".") / path_str

            if not model_dir.exists() or not model_dir.is_dir():
                logger.warning(f"Configured model path '{path_str}' does not exist or is not a directory. Skipping...")
                continue

            logger.info(f"Scanning directory '{model_dir}' for models...")

            for ext in ("**/*.yml", "**/*.yaml"):
                for yml_path in model_dir.glob(ext):
                    model_name = yml_path.stem
                    try:
                        with yml_path.open("r", encoding="utf-8") as f:
                            model_data = yaml.safe_load(f)

                        if not isinstance(model_data, dict):
                            logger.error(f"Invalid model configuration in '{yml_path}'. Expected a dictionary but got {type(model_data).__name__}.")
                            continue

                        model_config = ModelConfig(**model_data)

                        if model_name in manifest:
                            logger.warning(f"Model '{model_name}' is already defined. Overwriting with configuration from '{yml_path}'.")

                        manifest[model_name] = model_config
                        logger.debug(f"Successfully loaded model '{model_name}' from '{yml_path}'.")

                    except yaml.YAMLError as exc:
                        logger.error(f"Error parsing YAML file '{yml_path}': {exc}")
                    except Exception as exc:
                        logger.error(f"Unexpected error loading model from '{yml_path}': {exc}")

        logger.info(f"Successfully loaded {len(manifest)} models into the manifest.")
        return manifest

    def save(self, manifest: Dict[str, ModelConfig]) -> None:
        """
        Saves the manifest dictionary as a JSON file in the target directory specified
        by the project config, under a `manifest` subfolder.

        Args:
            manifest (Dict[str, ModelConfig]): The manifest to save.
        """
        target_path = Path(self.project_config.target_path)
        manifest_dir = target_path / "manifest"
        manifest_dir.mkdir(parents=True, exist_ok=True)

        manifest_file = manifest_dir / "manifest.json"

        manifest_data = {name: model.model_dump() for name, model in manifest.items()}

        try:
            with manifest_file.open("w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=4, ensure_ascii=False)
            logger.info(f"Manifest successfully written to {manifest_file}")
        except Exception as exc:
            logger.error(f"Failed to write manifest to {manifest_file}: {exc}")

def execute_load_manifest() -> Dict[str, ModelConfig]:
    """
    Executes the overall process of loading the project configuration,
    building the manifest, and saving it to the target directory.

    Returns:
        Dict[str, ModelConfig]: The loaded manifest.
    """
    try:
        config_loader = ProjectLoader()
        project_config = config_loader.load_gbt_project_config()
    except Exception as e:
        logger.error(f"Failed to load project configuration: {e}")
        raise

    manifest_loader = ManifestLoader(project_config)
    manifest = manifest_loader.load()
    manifest_loader.save(manifest)

    return manifest
