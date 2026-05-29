from core.gbt.engine.base.destination import BaseCypherEngine
from typing import Any, Dict, Optional
from core.gbt.parser.manifest.loader import execute_load_manifest
from core.gbt.common.gbt import write_ddl_compile_cypher, load_manifest_config
from jinja2 import Environment, PackageLoader
from connectors.neo4j import Neo4jConnector
import logging

# Configure basic logger
logger = logging.getLogger(__name__)

class DeleteEngine(BaseCypherEngine):
    """
    DeleteEngine is responsible for handling deletion operations in Neo4j.
    It compiles the Cypher DML statements for deleting nodes, relation data, labels,
    or constraints based on the model configuration and executes them against the database.
    """

    SUPPORTED_TEMPLATES = {
        'node': 'destinations/neo4j/dml/delete_node.cypher.j2',
        'label': 'destinations/neo4j/dml/delete_label.cypher.j2',
        'constraint': 'destinations/neo4j/dml/delete_constraint.cypher.j2',
        'relationship': 'destinations/neo4j/dml/delete_relation.cypher.j2'
    }

    def __init__(self, model_name: str, object_type: str, connector: Optional[Neo4jConnector] = None):
        """
        Initializes the DeleteEngine with the target model and object type.

        Args:
            model_name (str): The name of the model present in the manifest.
            object_type (str): The type of object to delete ('node', 'label', 'constraint', or 'relationship').
            connector (Optional[Neo4jConnector]): An active Neo4j connector instance. Defaults to None.
        """
        super().__init__()
        self.model_name = model_name
        self.object_type = object_type.lower()
        self._validate_object_type()

        self.manifest = self._load_manifest()
        self.model_config = self._get_model_config()
        self.physical_name = self.model_config.get('models', {}).get('physical_name', self.model_name)
        self.neo4j_connector = connector or Neo4jConnector()

    def _validate_object_type(self) -> None:
        """
        Validates the provided object type against the supported templates.

        Raises:
            ValueError: If the object_type is not defined within SUPPORTED_TEMPLATES.
        """
        if self.object_type not in self.SUPPORTED_TEMPLATES:
            valid_types = ", ".join(self.SUPPORTED_TEMPLATES.keys())
            error_msg = f"\033[91mUnsupported object type '{self.object_type}'. Supported types are: {valid_types}\033[0m"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _load_manifest(self) -> Dict[str, Any]:
        """
        Loads and retrieves the overall project manifest configuration.

        Returns:
            Dict[str, Any]: The loaded manifest configuration mapping.
        """
        execute_load_manifest()
        return load_manifest_config()

    def _get_model_config(self) -> Dict[str, Any]:
        """
        Retrieves the specific data model configuration from the manifest.

        Returns:
            Dict[str, Any]: The configuration properties for the assigned model.

        Raises:
            KeyError: If the model_name is not found in the loaded manifest mapping.
        """
        if self.model_name not in self.manifest:
            error_msg = f"\033[91mModel '{self.model_name}' not found in manifest.\033[0m"
            logger.error(error_msg)
            raise KeyError(error_msg)
        return self.manifest[self.model_name]

    def _prepare_template_context(self, constraint_name: Optional[str]) -> tuple[Dict[str, Any], str]:
        """
        Prepares the underlying Jinja rendering context and the generated compilation suffix.

        Args:
            constraint_name (Optional[str]): The explicit constraint name (Required if object_type is 'constraint').

        Returns:
            tuple[Dict[str, Any], str]: A tuple comprising the template context dictionary
            and a formatted string indicating the desired name suffix for the compiled Cypher query execution stream.

        Raises:
            ValueError: If 'object_type' is defined as 'constraint' but 'constraint_name' lacks a valid value.
        """
        context = {'node_label': self.model_name}
        compile_name_suffix = self.object_type

        if self.object_type == 'constraint':
            if not constraint_name:
                error_msg = "\033[91m'constraint_name' must be provided when object_type is 'constraint'.\033[0m"
                logger.error(error_msg)
                raise ValueError(error_msg)
            context['constraint_name'] = constraint_name
            compile_name_suffix = constraint_name

        elif self.object_type == 'relationship':
            context['physical_name'] = self.physical_name

        compile_model_name = f"{self.model_name}_{compile_name_suffix}_delete"
        return context, compile_model_name

    def compile(self, constraint_name: Optional[str] = None) -> str:
        """
        Compiles the necessary Cypher DML statement for deletion utilizing resolved object types and manifest configs.

        This method extracts the correct Jinja template, interpolates it with processed contexts, and outputs the
        prepared script directly to the pre-configured project target path.

        Args:
            constraint_name (Optional[str]): The associated rule/constraint identity to resolve if required. Defaults to None.

        Returns:
            str: The fully formatted and compiled DML Cypher deletion inquiry script.

        Raises:
            ValueError: If validation properties or strict relational definitions map improperly during rendering.
            Exception: Unhandled pipeline integration failures triggered by templating configurations or I/O processes.
        """
        logger.info(f"Starting compilation for delete DML query - model: {self.model_name}, type: {self.object_type}")
        try:
            env = Environment(loader=PackageLoader('core.gbt', 'templates'))
            template = env.get_template(self.SUPPORTED_TEMPLATES[self.object_type])

            context, compile_model_name = self._prepare_template_context(constraint_name)
            cypher_delete_query = template.render(**context)

            logger.debug(f"Rendered Cypher Query:\n{cypher_delete_query}")

            write_ddl_compile_cypher(
                cypher_statements=cypher_delete_query,
                model_path=self.model_name,
                ddl_cypher_path='cypher_dml',
                compile_model_name=compile_model_name,
                file_type='cypher'
            )

            logger.info(f"\033[92mSuccessfully compiled delete DML statement for model '{self.model_name}'.\033[0m")
            return cypher_delete_query

        except Exception as e:
            logger.error(f"\033[91mError compiling delete DML statement for model '{self.model_name}': {e}\033[0m", exc_info=True)
            raise

    def execute(self, constraint_name: Optional[str] = None) -> None:
        """
        Orchestrates compiling and effectively triggering the compiled target DML queries against the established platform connection endpoints.

        Args:
            constraint_name (Optional[str]): Specialized referential bounds identity when triggering rule isolation drops. Defaults to None.

        Raises:
            Exception: In situations when upstream dependency triggers flag relational or integrity breakdown from Neo4j DB processes.
        """
        logger.info(f"Starting compilation and execution of delete DML query for model '{self.model_name}'...")
        try:
            cypher_delete_query = self.compile(constraint_name=constraint_name)

            logger.info(f"\033[93mExecuting delete operation for {self.object_type} on '{self.model_name}'...\033[0m")

            self.neo4j_connector.run_query(query=cypher_delete_query)

            target_identity = constraint_name if self.object_type == 'constraint' else self.model_name
            logger.info(f"\033[92mSuccessfully executed delete DML for {self.object_type} '{target_identity}'.\033[0m")

        except Exception as e:
            logger.error(f"\033[91mError executing delete operation for model '{self.model_name}': {e}\033[0m", exc_info=True)
            raise
