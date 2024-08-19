import importlib
import importlib.util
import typing as t
from types import ModuleType

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed


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
            def ready(self):
                print("AppConfig is ready!")
        ```

        Returns:
            None
        """
        self.unfazed = unfazed
        self.app_module = app_module

    @property
    def name(self) -> str:
        return self.app_module.__name__.rsplit(".", 1)[0]

    @property
    def label(self) -> str:
        return self.name.replace(".", "_")

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

        return app_cls(unfazed, app_module)

    def ready(self):
        raise NotImplementedError("Subclasses must implement this method.")
