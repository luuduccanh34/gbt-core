from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Union

class PropertiesConfig(BaseModel):
    """
    Configuration for properties of a graph component (node or relationship).
    """
    name: str = Field(..., description="The name of the property.")
    data_type: Literal['string', 'integer', 'float', 'boolean', 'date', 'timestamp', 'datetime'] = Field(
        ..., description="The data type of the property."
    )
    description: Optional[str] = Field(None, description="An optional description of the property.")
    constraints: List[Literal['IS NOT NULL', 'IS UNIQUE']] = Field(
        default=[], description="A list of constraints applied to the property."
    )
    indexes: List[Literal['index', 'fulltext']] = Field(
        default=[], description="A list of indexes applied to the property."
    )

class ConnectedNodeConfig(BaseModel):
    """
    Configuration defining a node connection within a relationship.
    """
    label: str = Field(..., description="The label of the connected node.")
    join_key: str = Field(..., description="The key used to join the node.")

class NodeModelConfig(BaseModel):
    """
    Configuration model for a graph node.
    """
    type: Literal['node'] = Field(..., description="Identifier type for the model.")
    label: str = Field(..., description="The label of the node.")
    description: Optional[str] = Field(None, description="An optional description of the node.")
    properties: List[PropertiesConfig] = Field(..., description="A list of properties belonging to the node.")

class RelationModelConfig(BaseModel):
    """
    Configuration model for a graph relationship (edge).
    """
    type: Literal['relationship'] = Field(..., description="Identifier type for the model.")
    label: str = Field(..., description="The label or type of the relationship.")
    description: Optional[str] = Field(None, description="An optional description of the relationship.")
    properties: List[PropertiesConfig] = Field(
        ..., description="A list of properties belonging to the relationship."
    )

    source_node: ConnectedNodeConfig = Field(..., description="Configuration describing the source node.")
    target_node: ConnectedNodeConfig = Field(..., description="Configuration describing the target node.")

class ModelConfig(BaseModel):
    """
    Root configuration model that encapsulates either a node or a relationship configuration.
    """
    version: Optional[float] = Field(None, description="The version of the model configuration.")
    models: Union[NodeModelConfig, RelationModelConfig] = Field(
        ...,
        discriminator='type',
        description="The underlying graph model configuration, distinguished by its type."
    )
