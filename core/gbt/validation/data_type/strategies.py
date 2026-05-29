import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from core.gbt.exceptions.data_type.exceptions import DataTypeMismatchError, SkipRowException
from core.gbt.common.logging import Colors

logger = logging.getLogger(__name__)


class BaseErrorStrategy(ABC):
    """
    Abstract base class for data type validation error handling strategies.

    Strategies define how the system should react when a data type conversion fails
    for a specific column and row.
    """

    @abstractmethod
    def handle(
        self,
        row_index: int,
        col_name: str,
        raw_value: Any,
        target_dtype: str,
        original_exception: Exception,
        raw_row: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Handle a data type conversion error according to the chosen strategy.

        Args:
            row_index (int): The index of the row where the error occurred (1-based or 0-based).
            col_name (str): The name of the column that failed conversion.
            raw_value (Any): The original value that triggered the conversion error.
            target_dtype (str): The expected destination data type.
            original_exception (Exception): The raw exception raised during conversion attempt.
            raw_row (Dict[str, Any]): The complete row data in which the error occurred.

        Returns:
            Optional[Any]: A fallback value depending on the strategy (e.g., None).

        Raises:
            Exception: Depending on the strategy, it may raise a specialized exception.
        """
        pass


class FailFastStrategy(BaseErrorStrategy):
    """
    Strategy that immediately halts execution upon encountering a conversion error.
    It raises a clearly formatted DataTypeMismatchError.
    """

    def handle(
        self,
        row_index: int,
        col_name: str,
        raw_value: Any,
        target_dtype: str,
        original_exception: Exception,
        raw_row: Dict[str, Any]
    ) -> None:

        # Constructing a readable, colorized error message for terminal visibility
        error_msg = (
            f"{Colors.RED}{Colors.BOLD}Error at Row {row_index}:{Colors.RESET} "
            f"Failed to cast column '{Colors.CYAN}{col_name}{Colors.RESET}' with value "
            f"'{Colors.YELLOW}{raw_value}{Colors.RESET}' to '{Colors.GREEN}{target_dtype}{Colors.RESET}'."
        )

        logger.error(
            f"FailFastStrategy executed for row {row_index}, column '{col_name}'. "
            f"Halting execution. Original error: {original_exception}"
        )

        raise DataTypeMismatchError(
            message=error_msg,
            column_name=col_name,
            expected_type=target_dtype,
            actual_value=raw_value
        ) from original_exception


class NullifyStrategy(BaseErrorStrategy):
    """
    Strategy that ignores the conversion error and returns `None` for the problematic field,
    allowing the remainder of the dataset or row to continue processing seamlessly.
    """

    def handle(
        self,
        row_index: int,
        col_name: str,
        raw_value: Any,
        target_dtype: str,
        original_exception: Exception,
        raw_row: Dict[str, Any]
    ) -> Optional[Any]:

        logger.warning(
            f"{Colors.YELLOW}[NullifyStrategy]{Colors.RESET} Row {Colors.CYAN}{row_index}{Colors.RESET}: "
            f"Nullified column '{Colors.BOLD}{col_name}{Colors.RESET}' containing '{raw_value}'. "
            f"(Expected {target_dtype}). Reason: {original_exception}"
        )
        return None


class SkipRowStrategy(BaseErrorStrategy):
    """
    Strategy that signals the processor to entirely skip the current row when an error occurs,
    typically by raising a SkipRowException.
    """

    def handle(
        self,
        row_index: int,
        col_name: str,
        raw_value: Any,
        target_dtype: str,
        original_exception: Exception,
        raw_row: Dict[str, Any]
    ) -> None:

        skip_reason = (
            f"{Colors.YELLOW}{Colors.BOLD}Row {row_index} Skipped:{Colors.RESET} "
            f"Conversion failed in column '{Colors.CYAN}{col_name}{Colors.RESET}'. "
            f"Invalid value: '{raw_value}' (Expected '{target_dtype}')."
        )

        logger.warning(
            f"{Colors.YELLOW}[SkipRowStrategy]{Colors.RESET} Ignoring row {row_index}. "
            f"Failed on column '{col_name}'. Reason: {original_exception}"
        )

        raise SkipRowException(
            reason=skip_reason,
            row_data=raw_row
        ) from original_exception
