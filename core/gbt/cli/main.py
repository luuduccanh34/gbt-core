# core/gbt/cli/main.py
import importlib
from typing import List, Optional

import click

from .types import Command

TASK_MAPPING = {
    Command.COMPILE: "core.gbt.cli.commands.compile",
    Command.RUN: "core.gbt.cli.commands.run",
}


class GBTCLI(click.Group):
    """
    A custom command group that lazily loads commands from their respective modules.
    This keeps the CLI structure modular and improves startup performance.
    """

    def list_commands(self, ctx: click.Context) -> List[str]:
        """
        List all available commands defined in the TASK_MAPPING.

        Args:
            ctx (click.Context): The current click context.

        Returns:
            List[str]: A sorted list of available command string names.
        """
        return sorted([cmd.value for cmd in TASK_MAPPING.keys()])

    def get_command(self, ctx: click.Context, name: str) -> Optional[click.Command]:
        """
        Dynamically load and return a command's implementation.

        Args:
            ctx (click.Context): The current click context.
            name (str): The name of the command to execute.

        Returns:
            Optional[click.Command]: The loaded Click command, or None if an error occurs.
        """
        try:
            command_enum = Command.from_str(name)
        except ValueError:
            return None

        module_path = TASK_MAPPING.get(command_enum)
        if not module_path:
            click.secho(
                f"⚠️ Configuration Warning: Command '{name}' is defined in Enum but missing in TASK_MAPPING.",
                fg="yellow",
                bold=True,
                err=True
            )
            return None

        try:
            mod = importlib.import_module(module_path)
            command: click.Command = getattr(mod, command_enum.value)
            return command
        except ImportError as e:
            click.secho(
                f"❌ Import Error: Failed to load module '{module_path}'.\nDetails: {e}",
                fg="red",
                bold=True,
                err=True
            )
            return None
        except AttributeError as e:
            click.secho(
                f"❌ Attribute Error: Module '{module_path}' is missing the command function '{name}'.\nDetails: {e}",
                fg="red",
                bold=True,
                err=True
            )
            return None


@click.group(cls=GBTCLI)
def cli() -> None:
    """
    \b
    🚀 GBT (Graph Build Tool) CLI
    =============================
    A robust framework for orchestrating, compiling, and building graph data structures.

    This command-line interface serves as the primary entry point for all GBT operations.
    It utilizes a dynamic command loading mechanism to maintain performance and modularity.

    \b
    Common workflows include:
      - Validating and compiling graph models.
      - Executing and materializing structures into the target database.

    Use `gbt <command> --help` for detailed information about a specific command.
    """
    pass


if __name__ == "__main__":
    try:
        cli()
    except Exception as ex:
        click.secho(f"🔥 Unexpected Fatal Error: {ex}", fg="white", bg="red", bold=True, err=True)
