from core.gbt.engine.base.destination import BaseCypherEngine
from typing import Any, Dict, List
from core.gbt.parser.manifest.loader import execute_load_manifest
from core.gbt.common.gbt import write_ddl_compile_cypher, load_manifest_config
from jinja2 import Environment, PackageLoader
from connectors.neo4j import Neo4jConnector
import logging

# Configure basic logger
logger = logging.getLogger(__name__)

class InspectorEngine(BaseCypherEngine):
    """
    InspectorEngine is responsible for inspecting metadata (e.g. constraints)
    in Neo4j for a given model. It compiles and executes administrative/metadata
    Cypher queries based on the model configuration.
    """

    def __init__(self, model_name: str, object_type: str = 'node', connector: Any = None) -> None:
        """
        Initializes the InspectorEngine with the target model.

        Args:
            model_name (str): The name of the model corresponding to the Neo4j label/relationship.
            object_type (str): The type of the object ('node', 'label', 'relationship').
            connector (Neo4jConnector, optional): An initialized Neo4jConnector instance.

        Raises:
            KeyError: If the provided model name is not found in the manifest configuration.
        """
        super().__init__()
        self.model_name = model_name
        self.object_type = object_type.lower()
        self.manifest = self._load_manifest()

        # Load the configuration specific to the provided model
        if self.model_name not in self.manifest:
            error_msg = f"\033[91mModel '{self.model_name}' not found in manifest.\033[0m"
            logger.error(error_msg)
            raise KeyError(error_msg)

        self.model_config = self.manifest[self.model_name]
        self.physical_name = self.model_config.get('models', {}).get('physical_name', self.model_name)

        # Use the provided connector, or create a new one
        self.neo4j_connector = connector if connector else Neo4jConnector()

    def _load_manifest(self) -> Dict[str, Any]:
        """
        Loads and returns the manifest configuration.

        Returns:
            Dict[str, Any]: The parsed manifest configuration.
        """
        execute_load_manifest()
        return load_manifest_config()

    def compile(self) -> str:
        """
        Compiles the Cypher metadata query to fetch constraints for the model.

        This method uses Jinja templates to render Cypher queries checking constraints
        associated with the node label. It writes the compiled statement to the
        target directory and returns the combined Cypher string.

        Returns:
            str: Compiled Cypher query for showing constraints.

        Raises:
            Exception: If an error occurs during template rendering or file writing.
        """
        logger.info(f"Starting compilation for show constraints query - model: {self.model_name}")
        try:
            env = Environment(loader=PackageLoader(
                package_name='core.gbt',
                package_path='templates'
            ))

            template_to_use = env.get_template('destinations/neo4j/meta/show_constraints.cypher.j2')

            target_label = self.model_name
            if self.object_type == 'relationship':
                target_label = self.physical_name

            # Render the template using node_label mapped to model_name
            cypher_query = template_to_use.render(
                node_label=target_label,
            )

            logger.debug(f"Rendered Cypher Query:\n{cypher_query}")

            # Write compiled statement to file system
            write_ddl_compile_cypher(
                cypher_statements=cypher_query,
                model_path=self.model_name,
                ddl_cypher_path='cypher_meta',
                compile_model_name=f"{self.model_name}_show_constraints",
                file_type='cypher'
            )

            logger.info(f"\033[92mSuccessfully compiled show constraints query for model '{self.model_name}'.\033[0m")
            return cypher_query

        except Exception as e:
            logger.error(f"\033[91mError compiling show constraints query for model '{self.model_name}': {e}\033[0m", exc_info=True)
            raise

    def execute(self) -> List[Dict[str, Any]]:
        """
        Executes the compiled query to fetch constraint data in Neo4j.

        This method compiles the Cypher query and submits it to the Neo4j database
        using the Neo4j connector.

        Returns:
            List[Dict[str, Any]]: The result records containing constraint information.

        Raises:
            Exception: If an error occurs during the execution of the query.
        """
        logger.info(f"Starting execution of show constraints query for model '{self.model_name}'...")
        try:
            cypher_query = self.compile()

            logger.info(f"\033[93mFetching constraints for '{self.model_name}'...\033[0m")
            results = self.neo4j_connector.run_query(
                query=cypher_query
            )
            logger.info(f"\033[92mSuccessfully executed show constraints query for model '{self.model_name}'. Found {len(results)} constraints.\033[0m")

            return results

        except Exception as e:
            logger.error(f"\033[91mError executing show constraints query for model '{self.model_name}': {e}\033[0m", exc_info=True)
            raise
