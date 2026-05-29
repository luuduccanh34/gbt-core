import logging
from typing import Dict, List, Any, Optional
from jinja2 import Environment, PackageLoader

from core.gbt.engine.base.destination import BaseCypherEngine
from core.gbt.common.gbt import write_ddl_compile_cypher, load_manifest_config
from core.gbt.parser.manifest.loader import execute_load_manifest
from connectors.neo4j import Neo4jConnector



logger = logging.getLogger(__name__)

class SchemaBuilderEngine(BaseCypherEngine):
    """
    Cypher engine implementation for Data Definition Language (DDL) operations.

    This engine is responsible for extracting configuration details and generating
    Cypher constraints and indexes based on the provided model definitions. It natively
    supports both 'node' and 'relationship' object types.
    """

    def __init__(self, model_name: str):
        """
        Initializes the SchemaBuilderEngine with a given model configuration.

        Args:
            model_name (str): The name of the specific model to process,
                              typically corresponding to a manifest key.

        Raises:
            KeyError: If mandatory keys (like 'models' or 'label') are missing
                      from the provided configuration.
        """
        super().__init__()
        # Load the manifest and extract the configuration for the specified model
        manifest = self._load_manifest()
        if model_name not in manifest:
            error_msg = f"Model '{model_name}' not found in manifest."
            logger.error(error_msg)
            raise KeyError(error_msg)

        self._model_config = manifest[model_name]

        if 'models' not in self._model_config:
            error_msg = f"Invalid configuration for model '{model_name}': missing strictly required 'models' key."
            logger.error(error_msg)
            raise KeyError(error_msg)

        try:
            model_def = self._model_config['models']
            self._label = model_def['label']
            self._type = model_def.get('type', 'node').lower()
            self._properties = model_def.get('properties', [])

            # Resolve physical name based on graph component type
            if self._type == 'relationship':
                self._physical_name = model_def.get('physical_name', self._label)
            elif self._type == 'node':
                self._physical_name = self._label
            else:
                logger.warning(
                    f"Unknown model type '{self._type}' for model '{model_name}'. "
                    f"Defaulting physical name to label '{self._label}'."
                )
                self._physical_name = self._label

            self.neo4j_connector = Neo4jConnector()
        except KeyError as e:
            logger.error(f"Missing required key in model definition for '{model_name}': {e}")
            raise

    def _load_manifest(self) -> Dict[str, Any]:
        """
        Loads and returns the manifest configuration.
        """
        execute_load_manifest()
        return load_manifest_config()

    @property
    def label(self) -> str:
        """str: The primary label or identifier for the given model."""
        return self._label

    @property
    def type(self) -> str:
        """str: The structural type of the model (e.g., 'node', 'relationship')."""
        return self._type

    @property
    def physical_name(self) -> str:
        """str: The physical name of the graph component in Neo4j (often equal to label)."""
        return self._physical_name

    @property
    def properties(self) -> List[Dict[str, Any]]:
        """List[Dict[str, Any]]: A list of property definitions associated with the model."""
        return self._properties

    def extract(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extracts constraints and indexes from the model's properties configuration.

        Returns:
            Dict: A dictionary containing lists of extracted schema requirements:
                  - 'constraints': List of dictionaries mapping column to constraints.
                  - 'indexes': List of dictionaries mapping column to indexes.
        """
        logger.debug(f"Extracting DDL configuration for model: {self.label}")

        extracted_constraints = []
        extracted_indexes = []

        for prop in self.properties:
            column_name = prop.get('name')
            if not column_name:
                continue

            constraints = prop.get('constraints', [])
            indexes = prop.get('indexes', [])

            if constraints:
                extracted_constraints.append({
                    'column': column_name,
                    'constraints': constraints
                })

            if indexes:
                extracted_indexes.append({
                    'column': column_name,
                    'indexes': indexes
                })

        return {
            "constraints": extracted_constraints,
            "indexes": extracted_indexes
        }

    def _generate_constraint_name(self, column: str, rule: str) -> str:
        """
        Generates a standardized, safe constraint name based on the model type.

        Args:
            column (str): The graph element property being constrained.
            rule (str): The rule being applied (e.g., 'IS UNIQUE').

        Returns:
            str: A formatted snake_case string representing the constraint name.
        """
        rule_suffix = str(rule).replace(' ', '_').lower()
        prefix = "rel" if self.type == "relationship" else "node"
        return f"constraint_{prefix}_{self.physical_name}_{column}_{rule_suffix}"

    def compile(self) -> List[Dict[str, str]]:
        """
        Compiles the model configuration into Cypher DDL statements.

        This method uses Jinja templates to render Cypher queries (e.g., constraints and indexes)
        based on the extracted model configuration. It writes each compiled statement to the
        target directory.

        Returns:
            List[Dict[str, str]]: A list of compiled DDL statements with their metadata (name and type).

        Raises:
            Exception: If an error occurs during rendering or writing the statements.
        """
        logger.info(f"Starting compilation for model: {self.label} (Type: {self.type})")
        cypher_statements = []

        try:
            env = Environment(loader=PackageLoader(
                package_name='core.gbt',
                package_path='templates')
            )
            constraint_template = env.get_template('destinations/neo4j/ddl/create_constraint.cypher.j2')

            extracted_data = self.extract()

            # Process and compile Constraints
            for constraint_info in extracted_data.get('constraints', []):
                column = constraint_info['column']
                for rule in constraint_info.get('constraints', []):
                    # Generate a clean identifier for the constraint
                    constraint_name = self._generate_constraint_name(column, rule)

                    logger.debug(f"Rendering constraint: {constraint_name}")

                    # Render the template
                    cypher_ddl = constraint_template.render(
                        constraint_name=constraint_name,
                        model_type=self.type,
                        label_or_type=self.physical_name,
                        property_name=column,
                        rule=rule
                    )

                    cypher_statements.append({
                        "query": cypher_ddl,
                        "name": constraint_name,
                        "type": "constraint"
                    })

                    # Write compiled statement to file system
                    write_ddl_compile_cypher(
                        cypher_statements=cypher_ddl,
                        model_path=self.label,
                        ddl_cypher_path='cypher_ddl',
                        compile_model_name=constraint_name,
                        file_type='cypher'
                    )

            # TODO: Implement Index compilation when index templates are added.

            logger.info(f"Successfully compiled {len(cypher_statements)} DDL statements for model '{self.label}'.")

            return cypher_statements

        except Exception as e:
            logger.error(f"Error compiling DDL statements for model '{self.label}': {e}", exc_info=True)
            raise

    def execute(self, connector: Optional[Neo4jConnector] = None) -> List[Dict[str, str]]:
        """
        Executes the compiled Cypher DDL statements against the target database.

        This method first runs compilation to retrieve the needed Cypher statements,
        then establishes a connection using the provided database connector (or initializes
        a default Neo4jConnector), and sequentially executes each statement.

        Args:
            connector (Optional[Neo4jConnector]): An active database connector instance.
                                                  Defaults to a new Neo4jConnector if not provided.

        Returns:
            List[Dict[str, str]]: A list of dictionaries representing successfully created schemas.

        Raises:
            Exception: If an error occurs during the compilation or execution phase.
        """
        logger.info(f"Starting execution of DDL statements for model '{self.label}'")
        executed_schemas = []

        try:
            # 1. Compile queries
            cypher_statements = self.compile()

            if not cypher_statements:
                logger.info(f"No DDL statements to execute for model '{self.label}'.")
                return executed_schemas

            # 2. Assign database connector
            db_connector = connector or self.neo4j_connector

            # 3. Execute sequentially
            success_count = 0
            total_statements = len(cypher_statements)

            for idx, item in enumerate(cypher_statements, start=1):
                statement = item["query"]
                schema_name = item["name"]
                schema_type = item["type"]
                logger.info(f"Executing statement {idx}/{total_statements} for model '{self.label}':\n{statement}")
                try:
                    db_connector.run_query(query=statement)
                    logger.info(f"Successfully executed statement {idx}/{total_statements}.")
                    executed_schemas.append(item)
                    success_count += 1
                except Exception as query_error:
                    logger.error(f"Failed to execute statement {idx}/{total_statements} for model '{self.label}'. Error: {query_error}", exc_info=True)
                    raise

            logger.info(f"Successfully executed {success_count}/{total_statements} DDL statements for model '{self.label}'.")
            return executed_schemas

        except Exception as e:
            logger.error(f"Execution process terminated with errors for model '{self.label}': {e}", exc_info=True)
            raise
