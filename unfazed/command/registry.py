import logging
import typing as t
from pathlib import Path

from click import Group

import unfazed
from unfazed.schema import Command
from unfazed.utils import import_string

from .base import BaseCommand

if t.TYPE_CHECKING:
    from unfazed.app import AppCenter  # pragma: no cover
    from unfazed.core import Unfazed  # pragma: no cover

logger = logging.getLogger("unfazed.command")


class Base(Group):
    """
    Base class for command groups in the Unfazed framework.

    This class extends Click's Group class and provides a foundation for creating
    command groups with command loading capabilities.

    Attributes:
        unfazed (Unfazed): Reference to the Unfazed application instance
    """

    @t.override
    def __init__(self, unfazed: "Unfazed", name: str) -> None:
        """
        Initialize a new command group.

        Args:
            unfazed: The Unfazed application instance
            name: The name of the command group
        """
        super().__init__(name=name)
        self.unfazed = unfazed

    def load_command(self, command: Command) -> None:
        """
        Load a command from its path and add it to the group.

        Args:
            command: The Command object containing the command information

        Raises:
            TypeError: If the command class is not a subclass of BaseCommand
            ImportError: If the command class cannot be imported
        """

        cls = import_string(command.path)

        if not issubclass(cls, BaseCommand):
            error_msg = f"Command at {command.path} must be a subclass of BaseCommand"
            logger.error(error_msg)
            raise TypeError(error_msg)

        escaped_name = command.stem.replace("_", "-")
        cmd = cls(self.unfazed, escaped_name, command.label)

        self.add_command(cmd)


class CommandCenter(Base):
    """
    Command Management Center for the Unfazed framework.

    This class is responsible for loading and managing all commands from both
    the Unfazed internal commands and the application center.

    The CommandCenter will:
    1. Load all internal commands from the unfazed.command.internal package
    2. Load all commands from each application in the app center

    Attributes:
        unfazed (Unfazed): Reference to the Unfazed application instance
        app_center (AppCenter): Reference to the application center
    """

    @t.override
    def __init__(self, unfazed: "Unfazed", app_center: "AppCenter", name: str) -> None:
        """
        Initialize a new command center.

        Args:
            unfazed: The Unfazed application instance
            app_center: The application center
            name: The name of the command center
        """
        super().__init__(unfazed=unfazed, name=name)
        self.app_center = app_center

    async def setup(self) -> None:
        """
        Set up the command center by loading all commands.

        This method loads commands from both the internal command directory
        and from each application in the app center.
        """

        # Load all the commands from the unfazed internal
        internal_commands = self.list_internal_command()
        for command in internal_commands:
            self.load_command(command)

        # Load all the commands from the app center
        app_commands_count = 0
        for app_name, app in self.app_center:
            app_commands = app.list_command()
            app_commands_count += len(app_commands)
            for command in app_commands:
                self.load_command(command)

        logger.debug(
            f"CommandCenter setup complete. Total commands loaded: {len(internal_commands) + app_commands_count}"
        )

    def list_internal_command(self) -> t.List[Command]:
        """
        List all internal commands from the unfazed.command.internal package.

        This method scans the internal command directory for Python files and
        creates Command objects for each one, excluding the 'startproject' command
        which is handled by the CliCommandCenter.

        Returns:
            A list of Command objects representing internal commands
        """
        ret: t.List[Command] = []
        internal_command_dir = Path(unfazed.__path__[0]) / "command" / "internal"

        for command_file in internal_command_dir.glob("*.py"):
            command_name = command_file.stem

            # Ignore the startproject command
            # It's a CLI command and should not be loaded
            if command_name == "startproject":
                continue

            path = f"unfazed.command.internal.{command_name}.Command"
            command = Command(
                path=path, stem=command_name, label="unfazed.command.internal"
            )

            ret.append(command)

        return ret


class CliCommandCenter(Base):
    """
    Command Management Center for CLI operations.

    This class is specifically designed for CLI operations and only loads
    the 'startproject' command, which is used for creating new projects.

    Attributes:
        unfazed (Unfazed): Reference to the Unfazed application instance
        cli_command (t.List[str]): List of CLI command names to load
    """

    def __init__(self, unfazed: "Unfazed") -> None:
        """
        Initialize a new CLI command center.

        Args:
            unfazed: The Unfazed application instance
        """
        super().__init__(unfazed=unfazed, name="unfazed-cli")
        self.cli_command = ["startproject"]

    def setup(self) -> None:
        """
        Set up the CLI command center by loading the startproject command.
        """
        cli_commands = self.list_cli_command()

        for command in cli_commands:
            self.load_command(command)

    def list_cli_command(self) -> t.List[Command]:
        """
        List all CLI commands from the unfazed.command.internal package.

        This method scans the internal command directory for Python files and
        creates Command objects only for those specified in the cli_command list.

        Returns:
            A list of Command objects representing CLI commands
        """
        ret: t.List[Command] = []
        internal_command_dir = Path(unfazed.__path__[0]) / "command" / "internal"

        for command_file in internal_command_dir.glob("*.py"):
            command_name = command_file.stem

            if command_name in self.cli_command:
                path = f"unfazed.command.internal.{command_name}.Command"
                command = Command(
                    path=path, stem=command_name, label="unfazed.command.internal"
                )

                ret.append(command)

        return ret
