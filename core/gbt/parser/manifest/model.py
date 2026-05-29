from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Literal, Union

DataType = Literal['string', 'integer', 'float', 'boolean', 'date', 'timestamp', 'datetime']
ConstraintType = Literal['IS NOT NULL', 'IS UNIQUE']
IndexType = Literal['index', 'fulltext']

class PropertiesConfig(BaseModel):
    """
    Configuration for properties of a graph component (node or relationship).
    """
    name: str = Field(
        ...,
        description="The name of the property."
    )
    data_type: DataType = Field(
        ...,
        description="The data type of the property."
    )
    description: Optional[str] = Field(
        None,
        description="An optional description of the property."
    )
    constraints: List[ConstraintType] = Field(
        default=[],
        description="A list of constraints applied to the property."
    )
    indexes: List[IndexType] = Field(
        default=[],
        description="A list of indexes applied to the property."
    )

class ConnectedNodeConfig(BaseModel):
    """
    Configuration defining a node connection within a relationship.
    """
    label: str = Field(
        ...,
        description="The label of the connected node."
    )
    key: str = Field(
        ...,
        description="Primary key of the connected node used for establishing relationships."
    )
    ref: str = Field(
        ...,
        description="Reference to the source and destination of the connected node, which can be a model name or a specific property path within the model."
    )


class ContractSchemaConfig(BaseModel):
    """
    Configuration for data contract schema enforcement.
    """
    enforced: bool = Field(
        ...,
        description="Indicates whether the schema contract is strictly enforced during pipeline execution."
    )

class SettingsModelConfig(BaseModel):
    """
    Additional settings and behaviors for graph model processing.
    """
    contract: Optional[ContractSchemaConfig] = Field(
        None,
        description="Configuration and rules for contract schema enforcement."
    )
    on_schema_error: Optional[Literal['fail', 'nullify', 'skip_row']] = Field(
        None,
        description="Defines the execution behavior when a schema validation error is encountered."
    )

class BaseGraphModelConfig(BaseModel):
    """
    Base configuration for graph components containing common attributes
    applicable to both nodes and relationships.
    """
    label: str = Field(
        ...,
        description="The primary label or entity type name of the graph component."
    )
    description: Optional[str] = Field(
        None,
        description="An optional human-readable description of the component's purpose."
    )
    settings: Optional[SettingsModelConfig] = Field(
        None,
        description="Additional configuration settings and execution rules for the model."
    )
    properties: List[PropertiesConfig] = Field(
        ...,
        description="A list of property configurations belonging to this graph component."
    )

class NodeModelConfig(BaseGraphModelConfig):
    """
    Configuration model for a graph node.
    """
    type: Literal['node'] = Field(
        ...,
        description="Identifier type for the model."
    )

class RelationModelConfig(BaseGraphModelConfig):
    """
    Configuration model for a graph relationship (edge).
    """
    type: Literal['relationship'] = Field(
        ...,
        description="Identifier type for the model."
    )
    physical_name: str = Field(
        ...,
        description="The physical name of the relationship (edge) connecting nodes."
    )
    source_node: ConnectedNodeConfig = Field(
        ...,
        description="Configuration describing the source node."
    )
    target_node: ConnectedNodeConfig = Field(
        ...,
        description="Configuration describing the target node."
    )

class ScriptConfig(BaseModel):
    """
    Configuration for the script associated with the model.
    """
    raw_script: Optional[str] = Field(
        None,
        description="Raw SQL/Cypher script written directly here."
    )
    file_path: Optional[str] = Field(
        None,
        description="Path to an external file containing the script."
    )
    connector: Optional[str] = Field(
        None,
        description="The connector configured within this script."
    )
    original_script: Optional[str] = Field(
        None,
        description="The script in its original format (e.g., SQL, Cypher), before any rendering or processing."
    )

    @model_validator(mode='after')
    def validate_script_source(self) -> 'ScriptConfig':
        if not self.raw_script and not self.file_path and not self.original_script:
            raise ValueError("Either 'raw_script', 'file_path', or 'original_script' must be provided.")
        return self

class ModelConfig(BaseModel):
    """
    Root configuration model that encapsulates either a node or a relationship configuration.
    """
    version: Optional[float] = Field(
        None,
        description="The version of the model configuration."
    )
    models: Union[NodeModelConfig, RelationModelConfig] = Field(
        ...,
        discriminator='type',
        description="The underlying graph model configuration, distinguished by its type."
    )
    script: ScriptConfig = Field(
        ...,
        description="The script configuration associated with the model."
    )
