from abc import ABC, abstractmethod
from typing import Any

class BaseSourceConnectorEngine(ABC):
    """
    Abstract base class for source connector engines.

    This class defines the mandatory interface for all source connectors,
    ensuring they implement necessary methods to connect to a data source,
    compile queries, and execute data retrieval operations.
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Establishes a connection to the data source.

        This method should be implemented by subclasses to handle the specific
        connection logic required for different types of data sources (e.g., databases,
        APIs, file systems).

        Raises:
            NotImplementedError: If the subclass fails to implement this method.
        """
        raise NotImplementedError("The connect method must be implemented by subclasses.")

    @abstractmethod
    def compile(self) -> Any:
        """
        Compiles the given state or queries for the data source before execution.

        This method handles the preparation and formatting of necessary
        configurations or scripts tailored to the specific source source.

        Returns:
            Any: The compiled artifact, such as a formatted query string or configuration object.

        Raises:
            NotImplementedError: If the subclass fails to implement this method.
        """
        raise NotImplementedError("The compile method must be implemented by subclasses.")

    @abstractmethod
    def execute(self, query: str, batch_size: int = 1000, **kwargs: Any) -> Any:
        """
        Executes a query against the connected data source.

        Args:
            query (str): The query string or command to execute on the source system.
            batch_size (int, optional): The number of records to process or fetch per batch. Defaults to 1000.
            **kwargs (Any): Additional specific parameters required by the target source engine.

        Returns:
            Any: The result set of the query execution, such as a cursor, dataframe, or iterator.

        Raises:
            NotImplementedError: If the subclass fails to implement this method.
        """
        raise NotImplementedError("The execute method must be implemented by subclasses.")
