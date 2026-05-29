from core.gbt.validation.data_type.strategies import BaseErrorStrategy, FailFastStrategy, SkipRowStrategy
from core.gbt.common.datetime import to_iso_format
from typing import Any


class TypeCaster:
    """
    Utility class responsible for casting raw data values into standardized data types.

    This class provides a centralized mapping of data type names to their respective
    casting functions. It supports standard types (string, integer, float, boolean)
    as well as date/time types which are standardized to ISO 8601 string formats.
    """
    __CASTING_MAPPING = {
        'string': str,
        'integer': int,
        'float': float,
        'boolean': bool,
        'date': to_iso_format,
        'datetime': to_iso_format,
        'timestamp': to_iso_format
    }

    @classmethod
    def cast(cls, value: Any, target_dtype: str) -> Any:
        """
        Cast a given value to the specified target data type.

        Args:
            value (Any): The raw value to be cast.
            target_dtype (str): The name of the target data type (e.g., 'integer', 'string', 'date').

        Returns:
            Any: The value successfully cast to the target type, or standardized format (like ISO strings for dates).

        Raises:
            ValueError: If the provided `target_dtype` is not supported in the mapping.
            Exception: Propagates casting exceptions (like TypeError or ValueError) if the underlying cast function fails.
        """
        caster = cls.__CASTING_MAPPING.get(target_dtype.lower())
        if not caster:
            raise ValueError(f"Unsupported target data type: '{target_dtype}'")

        return caster(value)
