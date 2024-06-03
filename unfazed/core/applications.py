import typing as t
from importlib import import_module
from threading import Lock

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import BaseRoute
from starlette.types import ASGIApp
from unfazed.app.registry import AppCenter
from unfazed.command import CommandCenter
from unfazed.conf import BaseSettings
from unfazed.middleware.registry import MiddleWareCenter
from unfazed.orm.registry import ModelCenter


class Unfazed(Starlette):
    version = "0.0.1"

    def __init__(
        self,
        debug: bool = False,
        routes: t.Sequence[BaseRoute] | None = None,
        middleware: t.Sequence[Middleware] | None = None,
    ) -> None:
        self._ready = False
        self._settings: BaseSettings = None
        self._app_center: AppCenter = None
        self._command_center: CommandCenter = None
        self._model_center: ModelCenter = None
        super().__init__(debug=debug, routes=routes, middleware=middleware)

    @property
    def settings(self) -> BaseSettings:
        if not self._settings:
            self.setup_settings()

        return self._settings

    @property
    def app_center(self) -> AppCenter:
        if not self._app_center:
            self.setup_app()

        return self._app_center

    @property
    def command_center(self) -> CommandCenter:
        if not self._command_center:
            self.setup_commands()

        return self._command_center

    @property
    def model_center(self) -> ModelCenter:
        if not self._model_center:
            self.setup_models()

        return self._model_center

    def setup_settings(self) -> None:
        self._settings = BaseSettings.setup()

    def setup_app(self):
        self._app_center = AppCenter(self, self.settings.INSTALLED_APPS)
        self._app_center.setup()

    def setup_commands(self):
        self._command_center = CommandCenter(
            unfazed=self,
            name=self.settings.PROJECT_NAME,
            commands=self.app_center.commands,
        )
        self._command_center.setup()

    def setup_models(self):
        # self._model_center = ModelCenter(
        #     unfazed=self,
        #     models=self.app_center.models,
        # )

        # TODO
        # wait for orm to be implemented
        pass

    def setup_middlewares(self):
        # load middlewares
        middleware_center = MiddleWareCenter(self.settings.MIDDLEWARE)
        middleware_center.setup()

        for m in middleware_center.middlewares:
            self.add_middleware(m)

    def setup_routes(self):
        # add routes from settings.ROOT_URLCONF
        root_url_module = import_module(self.settings.ROOT_URLCONF)

        if not hasattr(root_url_module, "urlpatterns"):
            raise ValueError("ROOT_URLCONF should have urlpatterns defined")

        for route in root_url_module.urlpatterns:
            # TODO
            # check if route is a valid route
            # check if route app is installed
            self.router.routes.append(route)

    def setup(self) -> None:
        """
        steps to setup the application
        """

        if self._ready:
            return
        with Lock():
            if self._ready:
                return

            self.setup_settings()
            self.setup_app()

            self.setup_commands()
            self.setup_models()

            self.setup_middlewares()
            self.setup_routes()

            self._ready = True

    def setup_cli(self):
        self._command_center = CommandCenter(unfazed=self)
        self._command_center.setup_cli()

    def execute_command_from_argv(self):
        self._command_center.main()

    def build_middleware_stack(self) -> ASGIApp:
        # debug = self.debug
        # error_handler = None
        # exception_handlers: dict[
        #     t.Any, t.Callable[[Request, Exception], Response]
        # ] = {}

        # for key, value in self.exception_handlers.items():
        #     if key in (500, Exception):
        #         error_handler = value
        #     else:
        #         exception_handlers[key] = value

        # middleware = (
        #     [Middleware(ServerErrorMiddleware, handler=error_handler, debug=debug)]
        #     + self.user_middleware
        #     + [
        #         Middleware(
        #             ExceptionMiddleware, handlers=exception_handlers, debug=debug
        #         )
        #     ]
        # )

        middleware = self.user_middleware

        app = self.router
        for cls, args, kwargs in reversed(middleware):
            app = cls(app=app, *args, **kwargs)
        return app
