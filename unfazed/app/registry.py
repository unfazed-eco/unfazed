import typing as t
from threading import Lock

from unfazed.app.base import AppConfig
from unfazed.utils.module_loading import import_string

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed


class AppCenter:
    def __init__(self, unfazed: "Unfazed", installed_apps: t.Sequence[str]) -> None:
        self.unfazed = unfazed
        self.installed_apps = installed_apps

        self._ready = False
        self._loading = False
        self._lock = Lock()
        self._app_list = []

        self.commands = []
        self.models = []
        # self.urls = []
        # self.admin_models = []

    def setup(self) -> None:
        if self._ready:
            return

        with self._lock:
            if self._ready:
                return

            if self._loading:
                raise RuntimeError("circular dependency detected")

            self._loading = True

            app_list: t.Sequence[AppConfig] = []
            for app_path in self.installed_apps:
                temp_app = self.load_app(app_path)

                self.register_commands(temp_app)
                self.register_models(temp_app)

                app_list.append(temp_app)

            self._app_list = app_list

            self._ready = True
            self._loading = False

        return None

    def load_app(self, app_path: str) -> AppConfig:
        if not app_path.endswith(".AppConfig"):
            app_path += ".app.AppConfig"
        app_cls: t.Type[AppConfig] = import_string(app_path)

        app: AppConfig = app_cls(self.unfazed)
        app.setup()

        return app

    def register_commands(self, app: AppConfig) -> None:
        self.commands.extend(app.commands)

    def register_models(self, app: AppConfig) -> None:
        # TODO
        # wait for orm registry to be implemented
        # validate there are no duplicate db_table
        # self.models.extend(app.models)
        pass
