from enum import Enum


class Command(Enum):
    """
    Enumeration of available CLI commands for the GBT ecosystem.

    These commands represent the primary actions that can be executed
    via the command-line interface.
    """
    BUILD = "build"
    COMPILE = "compile"
    RUN = "run"
    DEBUG = "debug"
    INIT = "init"
    DOCS = "docs"

    @classmethod
    def from_str(cls, s: str) -> "Command":
        """
        Converts a string representation into a valid Command enum instance.

        Args:
            s (str): The string representing the command name.

        Returns:
            Command: The corresponding Command enum member.

        Raises:
            ValueError: If the provided string does not match any valid command.
        """
        try:
            return cls(s)
        except ValueError:
            valid_commands = [cmd.value for cmd in cls]
            raise ValueError(f"'{s}' is not a valid Command. Valid commands are: {valid_commands}")
