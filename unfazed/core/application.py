import typing as t
from asyncio import Lock

from asgiref import typing as at
from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool

from unfazed import protocol as p
from unfazed.app import AppCenter
from unfazed.cache import caches
from unfazed.command import CliCommandCenter, CommandCenter
from unfazed.conf import UnfazedSettings, settings
from unfazed.orm import ModelCenter
from unfazed.route import parse_urlconf
from unfazed.utils import import_string


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
        self._model_center: ModelCenter = None

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

    @property
    def cli_command_center(self) -> CliCommandCenter:
        if hasattr(self, "_cli_command_center"):
            return self._cli_command_center
        else:
            cmd = CliCommandCenter(self)
            setattr(self, "_cli_command_center", cmd)
            return cmd

    @property
    def model_center(self) -> ModelCenter:
        if self._model_center is None:
            self._model_center = ModelCenter(
                self.settings.DATABASE,
                self.app_center,
            )
        return self._model_center

    def setup_routes(self):
        if not self.settings.ROOT_URLCONF:
            return
        # add routes from settings.ROOT_URLCONF
        for route in parse_urlconf(self.settings.ROOT_URLCONF, self.app_center):
            self.router.routes.append(route)

    def setup_middleware(self):
        if not self.settings.MIDDLEWARE:
            return
        for middleware in self.settings.MIDDLEWARE:
            cls = import_string(middleware)
            self.user_middleware.insert(0, cls)

    def setup_cache(self):
        cache = self.settings.CACHE
        if not cache:
            return

        for alias, conf in cache.items():
            backend_cls = import_string(conf.BACKEND)
            location = conf.LOCATION
            options = conf.OPTIONS
            cache = backend_cls(location, options)
            caches[alias] = cache

    def build_middleware_stack(
        self,
    ) -> at.ASGIApplication:
        middleware = self.user_middleware
        app = self.router
        for cls in reversed(middleware):
            print(cls)
            app = cls(self, app)
        return app

    async def setup(self) -> None:
        if self._ready:
            return

        async with Lock():
            if self._ready:
                return

            if self._loading:
                raise RuntimeError("Unfazed is already loading")

            self._loading = True

            """
            app center setup may be required for cache

            so we setup cache first
            """
            self.setup_cache()
            await self.app_center.setup()
            self.setup_routes()
            self.setup_middleware()
            await self.command_center.setup()
            await self.model_center.setup()

            self._ready = True
            self._loading = False

    async def setup_cli(self):
        if self._ready:
            return

        async with Lock():
            if self._ready:
                return

            if self._loading:
                raise RuntimeError("Unfazed is already loading")

            self._loading = True

            self.cli_command_center.setup()

            self._ready = True
            self._loading = False

    async def execute_command_from_argv(self):
        await run_in_threadpool(self.command_center.main)

    async def execute_command_from_cli(self):
        await run_in_threadpool(self.cli_command_center.main)
