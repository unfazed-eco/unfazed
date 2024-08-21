import typing as t
from threading import Lock

from starlette.applications import Starlette

from unfazed import protocol as p
from unfazed.app import AppCenter
from unfazed.command import CommandCenter
from unfazed.conf import UnfazedSettings, settings
from unfazed.route import parse_urlconf


class Unfazed(Starlette):
    version = "0.0.1"

    def __init__(
        self,
        debug: bool = False,
        routes: t.Sequence[p.Route] | None = None,
        middlewares: t.Sequence[p.MiddleWare] | None = None,
    ) -> None:
        self._ready = False
        self._loading = False

        self._app_center: AppCenter = None
        self._command_center: CommandCenter = None

        super().__init__(debug=debug, routes=routes, middleware=middlewares)

    @property
    def settings(self) -> UnfazedSettings:
        return settings["UNFAZED_SETTINGS"]

    @property
    def ready(self) -> bool:
        return self._ready

    @property
    def app_center(self) -> AppCenter:
        if self._app_center is None:
            self._app_center = AppCenter(self, self.settings.INSTALLED_APPS)
        return self._app_center

    @property
    def command_center(self) -> CommandCenter:
        if self._command_center is None:
            self._command_center = CommandCenter(
                self,
                self.app_center,
                self.settings.PROJECT_NAME,
            )
        return self._command_center

    def setup_routes(self):
        # add routes from settings.ROOT_URLCONF
        for route in parse_urlconf(self.settings.ROOT_URLCONF, self.app_center):
            self.router.routes.append(route)

    def setup(self) -> None:
        if self._ready:
            return

        with Lock():
            if self._ready:
                return

            if self._loading:
                raise RuntimeError("circular dependency detected when loading apps")

            self._loading = True

            self.app_center.setup()
            self.command_center.setup()
            self.setup_routes()

            self._ready = True
            self._loading = False

    def execute_command_from_argv(self):
        self.command_center.main()
