import typing as t
from pathlib import Path

import unfazed
from click import Group
from unfazed.utils.module_loading import import_string

from .base import BaseCommand

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed


class CommandCenter(Group):
    def __init__(
        self,
        unfazed: "Unfazed",
        name: str | None = None,
        commands: t.List[BaseCommand] | None = None,
    ) -> None:
        if commands is None:
            commands = []
        super().__init__(name=name, commands={c.name: c for c in commands})
        self.unfazed = unfazed
        self._ready = False

    def add_base_commands(self, include: t.Sequence[str] | None = None) -> None:
        enable_include = include is not None
        include = include or []
        internal_command_dir = Path(unfazed.__path__[0] + "/command/internal")
        for command_file in internal_command_dir.glob("*.py"):
            command_name = command_file.stem
            if command_name == "__init__":
                continue
            if enable_include and command_name not in include:
                continue
            command_kls: BaseCommand = import_string(
                f"unfazed.command.internal.{command_name}.Command"
            )

            escaped = command_name.replace("_", "-")
            cmd = command_kls(
                unfazed=self.unfazed,
                app_label="unfazed.command.internal",
                name=escaped,
            )
            self.add_command(cmd)

    def setup(self):
        if self._ready:
            return
        self.add_base_commands()

        self._ready = True
        return None

    def setup_cli(self):
        self.add_base_commands(include=["startproject"])
