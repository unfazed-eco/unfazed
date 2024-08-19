import typing as t
from threading import Lock

from unfazed.type import InstalledApps

from .base import BaseAppConfig

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed


class AppCenter:
    def __init__(self, unfazed: "Unfazed", installed_apps: InstalledApps) -> None:
        self.unfazed = unfazed
        self.installed_apps = installed_apps

        self._ready = False
        self._loading = False
        self._lock = Lock()

        self._store: t.Dict[str, BaseAppConfig] = {}

    def setup(self) -> None:
        if self._ready:
            return

        with self._lock:
            if self._ready:
                return

            if self._loading:
                raise RuntimeError("circular dependency detected when loading apps")

            self._loading = True

            for app_path in self.installed_apps:
                if app_path in self._store:
                    raise RuntimeError(f"App with path {app_path} is already loaded")
                temp_app = self.load_app(app_path)

                self._store[temp_app.name] = temp_app

            self._ready = True
            self._loading = False

        return None

    def load_app(self, app_path: str) -> BaseAppConfig:
        app_config = BaseAppConfig.from_entry(app_path, self.unfazed)
        return app_config
