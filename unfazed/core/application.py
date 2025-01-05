import typing as t

from starlette.concurrency import run_in_threadpool
from starlette.datastructures import State
from starlette.routing import Router
from starlette.types import ASGIApp, Receive, Scope, Send

from unfazed import protocol as p
from unfazed.app import AppCenter
from unfazed.cache import caches
from unfazed.command import CliCommandCenter, CommandCenter
from unfazed.conf import UnfazedSettings
from unfazed.conf import settings as settings_proxy
from unfazed.db import ModelCenter
from unfazed.lifespan import BaseLifeSpan, lifespan_context, lifespan_handler
from unfazed.logging import LogCenter
from unfazed.openapi import OpenApi
from unfazed.openapi.routes import patterns
from unfazed.route import Route, parse_urlconf
from unfazed.schema import LogConfig
from unfazed.utils import import_string, unfazed_locker


class Unfazed:
    """
    Core Asgi Application implementation

    Usage:

    ```python

    import os
    from unfazed import Unfazed

    async def main():

        os.environ["UNFAZED_SETTINGS_MODULE"] = "path.to.settings"
        app = Unfazed()
        await app.setup()

    ```

    Step to setup Unfazed:

    1. setup settings
        unfazed loads settings from os.environ["UNFAZED_SETTINGS_MODULE"], see `unfazed.conf.UnfazedSettings`

    2. setup logging
        unfazed setup logging from settings.LOGGING, unfazed has default logging config
        and default config will merge with settings.LOGGING

    3. setup cache
        unfazed setup cache from settings.CACHE
        unfazed provide two cache backend: Memory Backend, Redis Backend
        if settings.CACHE is empty, unfazed will skip

    4. setup app center
        unfazed setup app center from settings.INSTALLED_APPS
        unfazed loop through all apps and call app.setup()

    5. setup model center
        unfazed setup model center from settings.DATABASE
        now unfazed only support tortoise orm

    6. setup routes
        unfazed use settings.ROOT_URLCONF to setup routes as the entry point
        then loop through all apps and extract routes from app.routes

    7. setup middleware
        unfazed setup middleware from settings.MIDDLEWARE

    8. setup command center
        unfazed loop through all apps and extract commands from app.commands

    9. setup lifespan
        unfazed setup lifespan from settings.LIFESPAN

    10. setup openapi
        unfazed setup openapi from settings.OPENAPI

    """

    def __init__(
        self,
        *,
        routes: t.List[Route] | None = None,
        middlewares: t.List[t.Type[p.MiddleWare]] | None = None,
        settings: UnfazedSettings | None = None,
    ) -> None:
        self._ready = False
        self._loading = False

        self._app_center: AppCenter | None = None
        self._command_center: CommandCenter | None = None
        self._model_center: ModelCenter | None = None

        # convinient for building test
        if settings:
            settings_proxy["UNFAZED_SETTINGS"] = settings
        self._settings = settings

        self.state = State()
        self.router = Router(routes)
        self.user_middleware = middlewares or []
        self.middleware_stack: ASGIApp | None = None

    @property
    def debug(self) -> bool:
        return self.settings.DEBUG

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

    @property
    def routes(self) -> t.List[Route]:
        return self.router.routes  # type: ignore

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self.ready:
            await self.setup()
        scope["app"] = self
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()
        await self.middleware_stack(scope, receive, send)

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
            cache_backend = backend_cls(location, options)
            caches[alias] = cache_backend

    def setup_logging(self) -> None:
        if not self.settings.LOGGING:
            config = {}

        else:
            config = LogConfig.model_validate(self.settings.LOGGING).model_dump(
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
            t.cast(t.List[Route], self.router.routes),
            self.settings.OPENAPI,
        )

        pattern: Route
        for pattern in patterns:  # type: ignore
            self.router.routes.append(pattern)

    def build_middleware_stack(self) -> ASGIApp:
        middleware = self.user_middleware
        app = self.router
        for cls in reversed(middleware):
            app = cls(app)  # type: ignore
        return app

    @unfazed_locker
    async def setup(self) -> None:
        """
        Setup Order is very important, refer above docstring for more info

        """
        self.setup_logging()
        self.setup_cache()
        await self.app_center.setup()
        await self.model_center.setup()
        self.setup_routes()
        self.setup_middleware()
        await self.command_center.setup()
        self.setup_lifespan()
        self.setup_openapi()

    @unfazed_locker
    async def setup_cli(self) -> None:
        self.cli_command_center.setup()

    async def execute_command_from_argv(self) -> None:
        await run_in_threadpool(self.command_center.main)

    async def execute_command_from_cli(self) -> None:
        await run_in_threadpool(self.cli_command_center.main)
