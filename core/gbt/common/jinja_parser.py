"""
Jinja template parser module.

Provides a JinjaParser class for rendering SQL/Cypher templates containing
GBT custom macros like `config` and `source`.
"""

import logging
from typing import Dict, Any, Tuple
import jinja2

logger = logging.getLogger(__name__)

class JinjaParser:
    """
    Parses and renders Jinja templates for GBT models.

    This class provides an isolated environment for rendering scripts
    with predefined macros such as `config` and `source`, and extracts
    the configuration dynamically during the rendering process.
    """

    def __init__(self) -> None:
        """
        Initializes the Jinja environment and registers global macros.
        """
        self.env = jinja2.Environment()
        self._extracted_config: Dict[str, Any] = {}

        # Register macros
        self.env.globals['config'] = self._config_macro
        self.env.globals['source'] = self._source_macro

    def _config_macro(self, **kwargs: Any) -> str:
        """
        Jinja macro to capture configuration values.

        Args:
            **kwargs: Configuration keys and values.

        Returns:
            str: An empty string to avoid rendering configuration blocks in the final script.
        """
        self._extracted_config.update(kwargs)
        return ""

    @staticmethod
    def _source_macro(catalog: str, schema: str, table: str) -> str:
        """
        Jinja macro to format a fully qualified source table name.

        Args:
            catalog (str): The catalog name.
            schema (str): The schema name.
            table (str): The table name.

        Returns:
            str: The fully qualified source table name formatted as 'catalog.schema.table'.
        """
        return f"{catalog}.{schema}.{table}"

    def parse(self, raw_template: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parses and renders the given Jinja template string.

        Args:
            raw_template (str): The raw Jinja template string to be rendered.

        Returns:
            Tuple[str, Dict[str, Any]]: A tuple containing the rendered script (str)
                                        and the extracted configuration (dict).

        Raises:
            jinja2.TemplateError: If rendering the template fails.
        """
        try:
            # Clear previous configs in case of instance reuse
            self._extracted_config.clear()
            template = self.env.from_string(raw_template)
            rendered_script = template.render()
            logger.debug("Successfully rendered Jinja template and extracted config.")
            return rendered_script, dict(self._extracted_config)
        except jinja2.TemplateError as exc:
            logger.error(f"Failed to render Jinja template: {exc}")
            raise
        except Exception as exc:
            logger.error(f"Unexpected error during template rendering: {exc}")
            raise
