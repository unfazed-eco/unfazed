import typing as t

from asgiref import typing as at
from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool

from unfazed import protocol as p
from unfazed.app import AppCenter
from unfazed.cache import caches
from unfazed.command import CliCommandCenter, CommandCenter
from unfazed.conf import UnfazedSettings
from unfazed.conf import settings as settings_proxy
from unfazed.db import ModelCenter
from unfazed.lifespan import lifespan_context, lifespan_handler
from unfazed.logging import LogCenter
from unfazed.openapi import OpenApi
from unfazed.openapi.routes import patterns
from unfazed.protocol import BaseLifeSpan
from unfazed.route import Route, parse_urlconf
from unfazed.schema import LogConfig
from unfazed.utils import import_string, unfazed_locker


class Unfazed(Starlette):
    def __init__(
        self,
        *,
        routes: t.Sequence[Route] | None = None,
        middlewares: t.Sequence[p.MiddleWare] | None = None,
        settings: UnfazedSettings | None = None,
    ) -> None:
        self._ready = False
        self._loading = False

        self._app_center: AppCenter = None
        self._command_center: CommandCenter = None
        self._model_center: ModelCenter = None

        # convinient for building test
        if settings:
            settings_proxy["UNFAZED_SETTINGS"] = settings
        self._settings = settings

        super().__init__(routes=routes, middleware=middlewares)

    @property
    def settings(self) -> UnfazedSettings:
        if self._settings is None:
            self._settings = settings_proxy["UNFAZED_SETTINGS"]
        return self._settings

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
                self,
                self.settings.DATABASE,
            )
        return self._model_center

    async def migrate(self) -> None:
        await self.model_center.migrate()

    def setup_routes(self) -> None:
        if not self.settings.ROOT_URLCONF:
            return
        # add routes from settings.ROOT_URLCONF
        for route in parse_urlconf(self.settings.ROOT_URLCONF, self.app_center):
            self.router.routes.append(route)

    def setup_middleware(self) -> None:
        if not self.settings.MIDDLEWARE:
            return
        for middleware in self.settings.MIDDLEWARE:
            cls = import_string(middleware)
            self.user_middleware.append(cls)

    def setup_cache(self) -> None:
        cache = self.settings.CACHE
        if not cache:
            return

        for alias, conf in cache.items():
            backend_cls = import_string(conf.BACKEND)
            location = conf.LOCATION
            options = conf.OPTIONS
            cache = backend_cls(location, options)
            caches[alias] = cache

    def setup_logging(self) -> None:
        if not self.settings.LOGGING:
            config = {}

        else:
            config = LogConfig(**self.settings.LOGGING).model_dump(
                exclude_none=True, by_alias=True
            )
        log_center = LogCenter(self, config)
        log_center.setup()

    def setup_lifespan(self) -> None:
        lifespan_handler.unfazed = self

        lifespan_list = self.settings.LIFESPAN or []

        for name in lifespan_list:
            cls = import_string(name)
            instance = cls(self)
            if not isinstance(instance, BaseLifeSpan):
                raise ValueError(f"{name} is not a valid lifespan")
            lifespan_handler.register(name, instance)

        self.router.lifespan_context = lifespan_context

    def setup_openapi(self) -> None:
        if not self.settings.OPENAPI:
            return

        OpenApi.create_schema(
            self.router.routes,
            self.settings.PROJECT_NAME,
            self.settings.VERSION,
            self.settings.OPENAPI,
        )
        for pattern in patterns:
            self.router.routes.append(pattern)

    def build_middleware_stack(
        self,
    ) -> at.ASGIApplication:
        middleware = self.user_middleware
        app = self.router
        for cls in reversed(middleware):
            app = cls(app)
        return app

    @unfazed_locker
    async def setup(self) -> None:
        """
        app center setup may be required for cache

        so we setup cache first
        """
        self.setup_logging()
        self.setup_cache()
        await self.app_center.setup()
        self.setup_routes()
        self.setup_middleware()
        await self.command_center.setup()
        await self.model_center.setup()
        self.setup_lifespan()
        self.setup_openapi()

    @unfazed_locker
    async def setup_cli(self) -> None:
        self.cli_command_center.setup()

    async def execute_command_from_argv(self) -> None:
        await run_in_threadpool(self.command_center.main)

    async def execute_command_from_cli(self) -> None:
        await run_in_threadpool(self.cli_command_center.main)

    def to_dict(self) -> t.Dict[str, t.Any]:
        return {
            "settings": self.settings.model_dump(),
            "routes": self.router.routes,
            "apps": self.app_center.store,
            "middlewares": self.user_middleware,
            "lifespan": lifespan_handler.lifespan,
            "commands": self.command_center.commands,
        }
