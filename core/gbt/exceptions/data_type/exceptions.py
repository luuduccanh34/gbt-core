"""
Data Type Exceptions

This module defines custom exceptions used for handling data type validation,
casting errors, and record-level skipping logic in the data pipeline.
"""

from typing import Any, Optional

class DataTypeError(Exception):
    """
    Base exception class for all data type related errors.

    This allows catching any data type specific error across the pipeline.
    """
    pass

class DataTypeMismatchError(DataTypeError):
    """
    Exception raised when a value cannot be converted or does not match the expected data type.
    """
    def __init__(
        self,
        message: str = "Data type mismatch occurred.",
        column_name: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Any = None
    ) -> None:
        """
        Initialize the DataTypeMismatchError.

        Args:
            message (str): A descriptive error message. Defaults to a generic message.
            column_name (str, optional): The name of the column where the mismatch occurred.
            expected_type (str, optional): The expected data type for the column.
            actual_value (Any, optional): The actual value that caused the mismatch.
        """
        self.column_name = column_name
        self.expected_type = expected_type
        self.actual_value = actual_value

        details = []
        if column_name:
            details.append(f"Column: '{column_name}'")
        if expected_type:
            details.append(f"Expected: '{expected_type}'")
        if actual_value is not None:
            # Safely get the type name of the actual value
            actual_type = type(actual_value).__name__
            details.append(f"Actual Value: '{actual_value}' (Type: {actual_type})")

        if details:
            full_message = f"{message} [{', '.join(details)}]"
        else:
            full_message = message

        super().__init__(full_message)

class SkipRowException(Exception):
    """
    Exception raised to signal that the current row should be skipped during processing.

    This is typically used in data parsing or validation steps where a non-critical error
    occurs, meaning only the specific record needs to be ignored instead of failing the entire batch.
    """
    def __init__(self, reason: str, row_data: Optional[Any] = None) -> None:
        """
        Initialize the SkipRowException.

        Args:
            reason (str): The specific reason why the row is being skipped.
            row_data (Any, optional): The original row data (e.g., dict or list) that triggered the skip.
        """
        self.reason = reason
        self.row_data = row_data

        message = f"Row skipped. Reason: {reason}"
        if row_data is not None:
             message += f" | Row Data: {row_data}"

        super().__init__(message)
