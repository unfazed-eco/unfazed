import typing as t

from unfazed.type import CanBeImported

from .base import BaseAppConfig

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class AppCenter:
    """
    Application Registry Manager for Unfazed Framework.

    This class manages the registration, loading, and lifecycle of applications
    within the Unfazed framework. It serves as a central registry for all
    installed applications and provides methods to access and manage them.

    Attributes:
        unfazed: The main Unfazed application instance
        installed_apps: List of application paths to be loaded
        _store: Internal dictionary storing loaded application configurations
    """

    def __init__(
        self, unfazed: "Unfazed", installed_apps: t.List[CanBeImported]
    ) -> None:
        """
        Initialize the AppCenter with the main Unfazed instance and installed apps.

        Args:
            unfazed: The main Unfazed application instance
            installed_apps: List of application paths to be loaded
        """
        self.unfazed = unfazed
        self.installed_apps = installed_apps
        self._store: t.Dict[str, BaseAppConfig] = {}

    async def setup(self) -> None:
        """
        Set up all installed applications.

        This method loads each application, initializes it, and stores it in the registry.
        It ensures that each application is loaded only once and properly initialized.
        Then it will wakeup settings modules.

        Raises:
            RuntimeError: If an application is already loaded
        """
        for app_path in self.installed_apps:
            if app_path in self._store:
                raise RuntimeError(f"App with path {app_path} is already loaded")
            temp_app = self.load_app(app_path)
            await temp_app.ready()
            temp_app.wakeup("settings")
            self._store[temp_app.name] = temp_app

    def load_app(self, app_path: str) -> BaseAppConfig:
        """
        Load an application from the given path.

        Args:
            app_path: The path to the application to load

        Returns:
            BaseAppConfig: The loaded application configuration
        """
        app_config = BaseAppConfig.from_entry(app_path, self.unfazed)
        return app_config

    def __getitem__(self, key: str) -> BaseAppConfig:
        """
        Get an application by its name.

        Args:
            key: The name of the application

        Returns:
            BaseAppConfig: The application configuration

        Raises:
            KeyError: If the application is not found
        """
        return self._store[key]

    def __contains__(self, key: str) -> bool:
        """
        Check if an application exists in the registry.

        Args:
            key: The name of the application to check

        Returns:
            bool: True if the application exists, False otherwise
        """
        return key in self._store

    def __iter__(self) -> t.Iterator[t.Tuple[str, BaseAppConfig]]:
        """
        Iterate over all registered applications.

        Returns:
            Iterator[tuple[str, BaseAppConfig]]: An iterator of (name, config) pairs
        """
        for key, value in self._store.items():
            yield (key, value)

    @property
    def store(self) -> t.Dict[str, BaseAppConfig]:
        """
        Get the internal store of application configurations.

        Returns:
            t.Dict[str, BaseAppConfig]: The dictionary of application configurations
        """
        return self._store
