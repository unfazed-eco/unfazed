import typing as t

from starlette.concurrency import run_in_threadpool
from starlette.datastructures import State
from starlette.routing import Router

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
from unfazed.type import ASGIApp, Receive, Scope, Send
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

    1. Settings - Load from UNFAZED_SETTINGS_MODULE environment variable
    2. Logging - Configure from settings.LOGGING with default fallback
    3. Cache - Setup from settings.CACHE (Memory/Redis backends)
    4. App Center - Initialize apps from settings.INSTALLED_APPS
    5. Model Center - Setup database from settings.DATABASE (Tortoise ORM)
    6. Routes - Configure from settings.ROOT_URLCONF and app routes
    7. Middleware - Load from settings.MIDDLEWARE
    8. Command Center - Collect commands from all apps
    9. Lifespan - Configure from settings.LIFESPAN
    10. OpenAPI - Setup from settings.OPENAPI
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
        self._cli_command_center: CliCommandCenter | None = None

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
        if self._cli_command_center is None:
            self._cli_command_center = CliCommandCenter(self)
        return self._cli_command_center

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
        routes = parse_urlconf(self.settings.ROOT_URLCONF, self.app_center)
        self.router.routes.extend(routes)

    def setup_middleware(self) -> None:
        if not self.settings.MIDDLEWARE:
            return
        self.user_middleware.extend(
            import_string(middleware) for middleware in self.settings.MIDDLEWARE
        )

    def setup_cache(self) -> None:
        if not (cache_settings := self.settings.CACHE):
            return

        for alias, conf in cache_settings.items():
            backend_cls = import_string(conf.BACKEND)
            caches[alias] = backend_cls(conf.LOCATION, conf.OPTIONS)

    def setup_logging(self) -> None:
        config = {}
        if self.settings.LOGGING:
            config = LogConfig.model_validate(self.settings.LOGGING).model_dump(
                exclude_none=True, by_alias=True
            )
        LogCenter(self, config).setup()

    def setup_lifespan(self) -> None:
        lifespan_handler.unfazed = self

        for name in self.settings.LIFESPAN or []:
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
        self.router.routes.extend(patterns)  # type: ignore

    def build_middleware_stack(self) -> ASGIApp:
        app = self.router
        for cls in reversed(self.user_middleware):
            app = cls(app)  # type: ignore
        return app

    @unfazed_locker
    async def setup(self) -> None:
        """Setup application components in order"""
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
