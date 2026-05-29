import json
import logging
import yaml
from pathlib import Path
from typing import Dict, Tuple

from .model import ModelConfig
from ..project.loader import ProjectLoader, GbtProjectConfig
from core.gbt.common.jinja_parser import JinjaParser

logger = logging.getLogger(__name__)
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
            self._process_model_directory(model_dir, manifest)

        logger.info(f"Successfully loaded {len(manifest)} models into the manifest.")
        return manifest

    def _process_model_directory(self, model_dir: Path, manifest: Dict[str, ModelConfig]) -> None:
        """
        Process all YAML files in a model directory to build the manifest.

        Args:
            model_dir (Path): The directory path to scan for YAML files.
            manifest (Dict[str, ModelConfig]): The manifest target to append loaded models to.
        """
        for ext in ("**/*.yml", "**/*.yaml"):
            for yml_path in model_dir.glob(ext):
                self._load_model_from_yaml(yml_path, model_dir, manifest)

    def _load_model_from_yaml(self, yml_path: Path, model_dir: Path, manifest: Dict[str, ModelConfig]) -> None:
        """
        Load a single model from a YAML file, resolving its script dependencies.

        Args:
            yml_path (Path): Path to the YAML model configuration.
            model_dir (Path): Root model directory for resolving relative scripts.
            manifest (Dict[str, ModelConfig]): Dictionary to register the resolved model.
        """
        try:
            with yml_path.open("r", encoding="utf-8") as f:
                model_data = yaml.safe_load(f)

            if not isinstance(model_data, dict):
                logger.error(f"Invalid model configuration in '{yml_path}'. Expected a dictionary but got {type(model_data).__name__}.")
                return

            if 'models' not in model_data or 'label' not in model_data['models']:
                logger.error(f"Missing required 'models.label' field in '{yml_path}'. Tracking failed.")
                return

            model_name = model_data['models']['label']

            # Find matching script file
            script_content, script_path_str = self._find_and_read_script_file(model_dir, model_name)
            original_script, connectors = JinjaParser().parse(script_content)

            if 'script' not in model_data or model_data['script'] is None:
                model_data['script'] = {}
            model_data['script']['raw_script'] = script_content
            model_data['script']['file_path'] = script_path_str
            model_data['script']['original_script'] = original_script.strip()
            model_data['script']['connector'] = connectors['connector']

            model_config = ModelConfig(**model_data)

            if model_name in manifest:
                logger.warning(f"Model '{model_name}' is already defined. Overwriting with configuration from '{yml_path}'.")

            manifest[model_name] = model_config
            logger.debug(f"Successfully loaded model '{model_name}' from '{yml_path}'.")

        except yaml.YAMLError as exc:
            logger.error(f"Error parsing YAML file '{yml_path}': {exc}")
            raise
        except Exception as exc:
            logger.error(f"Unexpected error loading model from '{yml_path}': {exc}")
            raise

    def _find_and_read_script_file(self, model_dir: Path, model_name: str) -> Tuple[str, str]:
        """
        Finds the corresponding SQL/Cypher/Txt script file for a given model name.
        Reads its content and returns a tuple (script_content, script_file_path).

        Args:
            model_dir (Path): The directory to search in.
            model_name (str): The name of the model to look up.

        Returns:
            Tuple[str, str]: Raw content of the script file and its string path.
        """
        found_script_files = []
        extensions = (".sql", ".cypher", ".txt")
        for script_ext in extensions:
            matches = list(model_dir.rglob(f"{model_name}{script_ext}"))
            found_script_files.extend(matches)

        if len(found_script_files) != 1:
            raise ValueError(
                f"Expected exactly one script file for model '{model_name}' in '{model_dir}', "
                f"but found {len(found_script_files)}: {[str(p) for p in found_script_files]}"
            )

        script_file = found_script_files[0]
        with script_file.open("r", encoding="utf-8") as f:
            script_content = f.read()

        return script_content, str(script_file)

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
