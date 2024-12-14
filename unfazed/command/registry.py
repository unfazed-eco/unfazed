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


class Base(Group):
    @t.override
    def __init__(self, unfazed: "Unfazed", name: str) -> None:
        super().__init__(name=name)
        self.unfazed = unfazed

    def load_command(self, command: Command) -> None:
        cls = import_string(command.path)

        if not issubclass(cls, BaseCommand):
            raise TypeError("Command must be a subclass of BaseCommand")

        escaped_name = command.stem.replace("_", "-")
        cmd = cls(
            self.unfazed,
            escaped_name,
            command.label,
        )

        self.add_command(cmd)


class CommandCenter(Base):
    """
    Command Manage Center

    CommandCenter will load all the commands from the unfazed internal and the app center

    """

    @t.override
    def __init__(self, unfazed: "Unfazed", app_center: "AppCenter", name: str) -> None:
        super().__init__(unfazed=unfazed, name=name)
        self.app_center = app_center

    async def setup(self) -> None:
        # load all the commands from the unfazed internal
        for command in self.list_internal_command():
            self.load_command(command)

        # load all the commands from the app center
        for _, app in self.app_center:
            for command in app.list_command():
                self.load_command(command)

    def list_internal_command(self) -> t.List[Command]:
        ret = []
        internal_command_dir = Path(unfazed.__path__[0] + "/command/internal")
        for command_file in internal_command_dir.glob("*.py"):
            command_name = command_file.stem

            # ignore the startproject command
            # its a cli command and should not be loaded
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

    Command Manage Center for CLI

    CLiCommandCenter only load the startproject command

    """

    def __init__(self, unfazed: "Unfazed") -> None:
        super().__init__(unfazed=unfazed, name="unfazed-cli")
        self.cli_command = ["startproject"]

    def setup(self) -> None:
        # load all the commands from the unfazed internal
        for command in self.list_cli_command():
            self.load_command(command)

    def list_cli_command(self) -> t.List[Command]:
        ret = []
        internal_command_dir = Path(unfazed.__path__[0] + "/command/internal")
        for command_file in internal_command_dir.glob("*.py"):
            command_name = command_file.stem

            if command_name in self.cli_command:
                path = f"unfazed.command.internal.{command_name}.Command"
                command = Command(
                    path=path, stem=command_name, label="unfazed.command.internal"
                )

                ret.append(command)

        return ret
