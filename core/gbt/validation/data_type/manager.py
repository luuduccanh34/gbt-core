from core.gbt.validation.data_type.caster import TypeCaster
from core.gbt.validation.data_type.strategies import BaseErrorStrategy, FailFastStrategy, SkipRowStrategy, NullifyStrategy
from core.gbt.exceptions.data_type.exceptions import DataTypeError, SkipRowException
from typing import Dict, Any, List
import logging

# Configure basic logging with colors for readability

logger = logging.getLogger(__name__)

class ValidationManager:
    """
    ValidationManager is responsible for validating and transforming batch data
    against predefined model properties and data types.

    It enforces the schema based on a specified error handling strategy.
    """

    def __init__(self, model_name: str, model_properties: List[Dict[str, Any]], on_schema_error: str = 'fail'):
        """
        Initializes the ValidationManager with the target schema and error handling strategy.

        Args:
            model_name (str): The name of the model being validated.
            model_properties (List[Dict[str, Any]]): The property definitions including expected data types.
            on_schema_error (str): Strategy for schema errors ('fail', 'nullify', 'skip_row').

        Raises:
            ValueError: If an unsupported `on_schema_error` value is provided.
        """
        self.model_name = model_name
        self.expected_properties = {
            prop.get('name'): prop.get('data_type')
            for prop in model_properties if prop.get('name') and prop.get('data_type')
        }

        strategy_map: Dict[str, BaseErrorStrategy] = {
            'fail': FailFastStrategy(),
            'nullify': NullifyStrategy(),
            'skip_row': SkipRowStrategy()
        }

        strategy_key = on_schema_error.lower()
        if strategy_key not in strategy_map:
            raise ValueError(
                f"Unsupported on_schema_error strategy: '{on_schema_error}'. "
                f"Must be one of: {', '.join(strategy_map.keys())}."
            )
        self.error_strategy = strategy_map[strategy_key]

    def process_batch(self, batch_index: int, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validates and cleans a batch of data by casting it to the expected data types.

        Args:
            batch_index (int): The index of the batch being processed.
            batch_data (List[Dict[str, Any]]): The raw batch data retrieved from the source.

        Returns:
            List[Dict[str, Any]]: A new list of cleaned, strongly-typed rows.

        Raises:
            KeyError: If a column in the data is missing from the model properties.
            DataTypeError: If a type casting fails and the strategy is to fail fast.
        """
        cleaned_batch: List[Dict[str, Any]] = []
        logger.info(f"Processing batch {batch_index} with {len(batch_data)} rows for model '{self.model_name}'.")

        for row_index, raw_row in enumerate(batch_data):
            cleaned_row: Dict[str, Any] = {}
            should_skip_row = False

            for col_name, raw_value in raw_row.items():
                if col_name not in self.expected_properties:
                    error_msg = f"Column '{col_name}' not defined in model properties for '{self.model_name}'"
                    logger.error(error_msg)
                    raise KeyError(error_msg)

                target_dtype = self.expected_properties[col_name]

                try:
                    cleaned_row[col_name] = TypeCaster.cast(raw_value, target_dtype)
                except (ValueError, TypeError) as original_error:
                    try:
                        resolved_value = self.error_strategy.handle(
                            row_index=row_index,
                            col_name=col_name,
                            raw_value=raw_value,
                            target_dtype=target_dtype,
                            original_exception=original_error,
                            raw_row=raw_row
                        )
                        cleaned_row[col_name] = resolved_value
                    except SkipRowException:
                        logger.warning(
                            f"\033[93mSkipping row {row_index} due to type error on '{col_name}': {original_error}\033[0m"
                        )
                        should_skip_row = True
                        break
                    except DataTypeError:
                        logger.error(
                            f"\033[91mData type error in row {row_index}, column '{col_name}': {original_error}\033[0m"
                        )
                        raise

            if not should_skip_row:
                cleaned_batch.append(cleaned_row)

        # Log success with green color for the schema comparison and data type validation
        logger.info(
            f"\033[92mSuccessfully finished processing data types for batch {batch_index}. "
            f"Cleaned rows: {len(cleaned_batch)}\033[0m"
        )

        return cleaned_batch
