from abc import ABC, abstractmethod
from typing import Any, List

class BaseCypherEngine(ABC):
    """
    Abstract base class for Cypher execution engines.

    This class defines the standard interface that any database-specific
    Cypher engine must implement to integrate with the GBT parsing framework.
    """

    @abstractmethod
    def compile(self) -> List[str]:
        """
        Compiles a model configuration into an executable Cypher query.

        Args:
        Returns:
            List[str]: Compiled Cypher statements ready for execution.

        Raises:
            NotImplementedError: If the subclass fails to implement this method.
        """
        raise NotImplementedError("The compile method must be implemented by subclasses.")

    @abstractmethod
    def execute(self, connector: Any = None) -> None:
        """
        Executes a given Cypher query against the target database.

        Args:
            connector (Any): Optional database connector used to execute statements.

        Raises:
            NotImplementedError: If the subclass fails to implement this method.
        """
        raise NotImplementedError("The execute method must be implemented by subclasses.")
