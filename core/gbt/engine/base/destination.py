from abc import ABC, abstractmethod

from core.gbt.parser.manifest.model import ModelConfig

class BaseCypherEngine(ABC):
    """
    Abstract base class for Cypher execution engines.

    This class defines the standard interface that any database-specific
    Cypher engine must implement to integrate with the GBT parsing framework.
    """

    @abstractmethod
    def compile(self, model_config: ModelConfig) -> str:
        """
        Compiles a model configuration into an executable Cypher query.

        Args:
            model_config (ModelConfig): The configuration of the model to compile.

        Returns:
            str: The fully compiled Cypher query string ready for execution.

        Raises:
            NotImplementedError: If the subclass fails to implement this method.
        """
        raise NotImplementedError("The compile method must be implemented by subclasses.")

    @abstractmethod
    def execute(self, cypher_query: str) -> None:
        """
        Executes a given Cypher query against the target database.

        Args:
            cypher_query (str): The Cypher query string to execute.

        Raises:
            NotImplementedError: If the subclass fails to implement this method.
        """
        raise NotImplementedError("The execute method must be implemented by subclasses.")
