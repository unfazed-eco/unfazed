import importlib
import importlib.util
import typing as t
import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from types import ModuleType

from unfazed.schema import Command

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class BaseAppConfig(ABC):
    """
    Base configuration class for Unfazed applications.

    This abstract class defines the interface and common functionality for all
    application configurations in the Unfazed framework. It provides methods for
    application initialization, command discovery, and module management.

    Usage:

    ```python
    # app.py

    from unfazed.app import BaseAppConfig

    class AppConfig(BaseAppConfig):
        async def ready(self):
            print("App is ready!")
    ```

    """

    def __init__(self, unfazed: "Unfazed", app_module: ModuleType) -> None:
        """
        Initialize the application configuration.

        Args:
            unfazed: The main Unfazed application instance
            app_module: The module containing the application code
        """
        self.unfazed = unfazed
        self.app_module = app_module

    @property
    def app_path(self) -> Path:
        """
        Get the filesystem path to the application module.

        Returns:
            Path: The absolute path to the application directory
        """
        if hasattr(self.app_module.__path__, "_path"):
            ret = Path(self.app_module.__path__._path[0])
        else:
            ret = Path(self.app_module.__path__[0])
        return ret

    @property
    def name(self) -> str:
        """
        Get the fully qualified name of the application module.

        Returns:
            str: The module name (e.g., 'myapp')
        """
        return self.app_module.__name__

    @property
    def label(self) -> str:
        """
        Get a label for the application, replacing dots with underscores.

        Returns:
            str: The application label (e.g., 'my_app')
        """
        return self.name.replace(".", "_")

    def list_command(self) -> t.List[Command]:
        """
        Discover and list all commands defined in the application.

        This method scans the 'commands' directory within the application
        and returns a list of Command objects for each Python file that
        doesn't start with an underscore.

        Returns:
            t.List[Command]: A list of discovered commands
        """
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
        """
        Check if the application has a models module.

        Returns:
            bool: True if the application has a models module, False otherwise
        """
        # check if models module exists
        existed = importlib.util.find_spec(f"{self.app_module.__name__}.models")

        return bool(existed)

    def wakeup(self, filename: str) -> bool:
        """
        Wake up the app by importing a specific module.

        This method attempts to import a module within the application,
        effectively "waking up" that part of the application.

        Args:
            filename: The name of the module to import (without .py extension)

        Returns:
            bool: True if the module was successfully imported, False otherwise
        """
        # check if the app has the given file
        try:
            importlib.import_module(f"{self.app_module.__name__}.{filename}")
            return True
        except ImportError:
            warnings.warn(
                f"Could not import {self.app_module.__name__}.{filename}, please check if the {filename} file exists.",
                stacklevel=2,
            )

            return False

    @classmethod
    def from_entry(cls, entry: str, unfazed: "Unfazed") -> t.Self:
        """
        Create an application configuration from an entry point.

        This factory method loads an application module and its configuration
        from a given entry point string.

        Args:
            entry: The entry point string (module path)
            unfazed: The main Unfazed application instance

        Returns:
            t.Self: An instance of the application configuration class

        Raises:
            ImportError: If the module specified in `entry` cannot be imported
            ModuleNotFoundError: If the `app.py` module cannot be found in the specified `entry` module
            AttributeError: If `AppConfig` is not found in the `app.py` module
            TypeError: If `AppConfig` is not a subclass of `BaseAppConfig`
        """
        try:
            module = importlib.import_module(entry)
        except Exception as err:
            raise ImportError(f"Could not import module {entry}") from err

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

    @abstractmethod
    async def ready(self) -> None:
        """
        Initialize the application when it's ready.

        This abstract method must be implemented by subclasses to perform
        any necessary initialization when the application is ready to run.
        """
        ...  # pragma: no cover

    def __str__(self) -> str:
        """
        Get a string representation of the application.

        Returns:
            str: The name of the application
        """
        return self.name
