import importlib
import importlib.util
import typing as t
import warnings
from pathlib import Path
from types import ModuleType

from unfazed.schema import Command

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class BaseAppConfig:
    def __init__(
        self,
        unfazed: "Unfazed",
        app_module: ModuleType,
    ) -> None:
        """
        Initialize the Config object.

        Args:
            unfazed (Unfazed): The Unfazed object.
            app_module (ModuleType): The app module.

        Usage:

        ```python
        # app.py

        from unfazed.app import BaseAppConfig
        class AppConfig(BaseAppConfig):
            async def ready(self):
                print("AppConfig is ready!")
        ```

        Returns:
            None
        """
        self.unfazed = unfazed
        self.app_module = app_module

    @property
    def app_path(self) -> Path:
        if hasattr(self.app_module.__path__, "_path"):
            ret = Path(self.app_module.__path__._path[0])
        else:
            ret = Path(self.app_module.__path__[0])
        return ret

    @property
    def name(self) -> str:
        return self.app_module.__name__

    @property
    def label(self) -> str:
        return self.name.replace(".", "_")

    def list_command(self) -> t.List[Command]:
        ret: t.List[Command] = []
        commands_path = self.app_path.joinpath("commands")
        if commands_path.exists() and commands_path.is_dir():
            command_file_list = commands_path.glob("*.py")

            for command_file in command_file_list:
                if command_file.stem.startswith("_"):
                    continue

                path = f"{self.name}.commands.{command_file.stem}.Command"
                ret.append(
                    Command(
                        path=path,
                        label=self.name,
                        stem=command_file.stem,
                    )
                )

        return ret

    def has_models(self) -> bool:
        # check if models module exists
        existed = importlib.util.find_spec(f"{self.app_module.__name__}.models")

        return bool(existed)

    def wakeup(self, filename: str) -> bool:
        """
        Wake up the app with the given label.

        Args:
            filename (str): The file of the app to wake up.

        Returns:
            bool
        """
        # check if the app has the given file
        try:
            importlib.import_module(f"{self.app_module.__name__}.{filename}")
            return True
        except ImportError:
            warnings.warn(
                f"Could not import {self.app_module.__name__}.{filename}, please check if the {filename} file exists."
            )

            return False

    @classmethod
    def from_entry(cls, entry: str, unfazed: "Unfazed") -> t.Self:
        """
        Load the configuration from the given entry module.

        Args:
            cls (type): The class of the configuration.
            entry (str): The entry module to import.
            unfazed (Unfazed): The Unfazed instance.

        Returns:
            Self: An instance of the configuration class.

        Raises:
            ImportError: If the module specified in `entry` cannot be imported.
            ModuleNotFoundError: If the `app.py` module cannot be found in the specified `entry` module.
            AttributeError: If `AppConfig` is not found in the `app.py` module.
            TypeError: If `AppConfig` is not a subclass of `BaseAppConfig`.
        """

        try:
            module = importlib.import_module(entry)
        except Exception:
            raise ImportError(f"Could not import module {entry}")

        # check if module has app submodule
        ret = importlib.util.find_spec(f"{module.__name__}.app")
        if ret is None:
            raise ModuleNotFoundError(f"Could not find app.py in {entry}")

        app_module = importlib.import_module(f"{module.__name__}.app")

        # check config class
        if not hasattr(app_module, "AppConfig"):
            raise AttributeError(f"AppConfig not found in {entry}.app")

        app_cls = app_module.AppConfig

        # check if AppConfig is a subclass of BaseAppConfig
        if not issubclass(app_module.AppConfig, cls):
            raise TypeError(
                f"{entry}.app.AppConfig must be a subclass of BaseAppConfig"
            )

        return app_cls(unfazed, module)

    async def ready(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def __str__(self) -> str:
        return self.name
