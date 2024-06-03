import importlib
import typing as t
import warnings
from pathlib import Path

from unfazed.command import BaseCommand
from unfazed.protocol import OrmModel
from unfazed.utils.module_loading import import_string

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed


class AppConfig:
    # name of the app
    # also the import path of the app
    name: str

    def __init__(self, unfazed: "Unfazed") -> None:
        self._ready = False
        self.commands = []
        self.models = []
        self.unfazed = unfazed

    @property
    def app_module(self) -> str:
        return self.__module__.rsplit(".", 1)[0]

    @property
    def app_path(self) -> Path:
        path = importlib.import_module(self.app_module).__path__._path[0]

        return Path(path)

    def setup(self) -> None:
        if self._ready:
            return

        # collect commands
        # list all files in the app/commands
        commands_path = self.app_path.joinpath("commands")

        if commands_path.exists() and commands_path.is_dir():
            command_file_list = commands_path.glob("*.py")

            commands = []
            for command_file in command_file_list:
                # check if BaseCommand is in the file
                path = f"{self.app_module}.commands.{command_file.stem}.Command"
                try:
                    command_cls = import_string(path)
                    if not issubclass(command_cls, BaseCommand):
                        raise ImportError("Not a valid command")

                except ImportError as e:
                    warnings.warn(
                        f"Command {command_file.stem} is not a valid command: err {e}"
                    )
                    continue

                commands.append(
                    command_cls(
                        self.unfazed,
                        app_label=self.name,
                        name=command_file.stem,
                    )
                )

            self.commands = commands

        # collect models
        # import all models from models module
        # models module may be models.py or models/__init__.py
        # all models should inherit from unfazed.orm.models.Model
        models: t.List[t.Type[OrmModel]] = []
        models_dir_path = self.app_path.joinpath("models")
        models_file_path = self.app_path.joinpath("models.py")
        # breakpoint()
        if models_dir_path.exists() or models_file_path.exists():
            models_module = importlib.import_module(f"{self.app_module}.models")
            for name in dir(models_module):
                obj = getattr(models_module, name)
                if isinstance(obj, type) and hasattr(obj, "meta"):
                    # if isinstance(obj, type) and issubclass(obj, OrmModel):
                    if not obj.meta.abstract:
                        models.append(obj)

            self.models = models

        # TODO
        # collect url/admin

        # exec ready method
        self.ready()

        self._ready = True

        return None

    def ready(self):
        pass
