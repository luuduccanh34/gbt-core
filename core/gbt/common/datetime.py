from datetime import datetime, date
from typing import Any

def to_iso_format(val: Any) -> str:
    """
    Converts a given date/time value into an ISO 8601 formatted string.

    Supports strings (ISO format), datetime objects, date objects,
    and numeric timestamps (int/float).

    Args:
        val (Any): The value to be converted.
            - str: An ISO 8601 formatted string (e.g., '2023-10-14T15:30:00Z').
            - datetime or date: A standard Python datetime or date object.
            - int or float: A UNIX timestamp.

    Returns:
        str: The ISO 8601 formatted string representation of the value.

    Raises:
        ValueError: If the input string cannot be parsed or the timestamp is invalid.
        TypeError: If the input type is 'None' or entirely unsupported.
    """
    if val is None:
        raise TypeError("Cannot cast 'None' to ISO format.")

    if isinstance(val, str):
        try:
            # Handle 'Z' for UTC representation correctly
            return datetime.fromisoformat(val.replace('Z', '+00:00')).isoformat()
        except ValueError as e:
            raise ValueError(f"Invalid ISO datetime string format '{val}': {e}")

    if isinstance(val, (datetime, date)):
        return val.isoformat()

    if isinstance(val, (int, float)):
        # Avoid treating boolean as int
        if isinstance(val, bool):
            raise TypeError("Unsupported type for ISO casting: bool")
        try:
            # Treat integer or float as a UNIX timestamp
            return datetime.fromtimestamp(val).isoformat()
        except (ValueError, OverflowError, OSError) as e:
            raise ValueError(f"Invalid numeric timestamp value '{val}': {e}")

    raise TypeError(f"Unsupported type for ISO casting: {type(val).__name__} (value: {val})")
