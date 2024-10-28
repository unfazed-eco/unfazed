import inspect
import typing as t

from starlette.middleware import Middleware
from starlette.routing import Route as StartletteRoute
from starlette.routing import compile_path

from unfazed.protocol import MiddleWare as MiddleWareProtocol
from unfazed.type import HttpMethod

from . import params as p
from . import utils as u
from .endpoint import EndPointDefinition, EndpointHandler


class Route(StartletteRoute):
    def __init__(
        self,
        path: str,
        endpoint: t.Callable[..., t.Any],
        *,
        methods: t.List[HttpMethod] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        middleware: t.Sequence[Middleware] | None = None,
        app_label: str | None = None,
        tags: t.List[str] | None = None,
        response_models: t.List[p.ResponseSpec] | None = None,
    ) -> None:
        if not path.startswith("/"):
            raise ValueError(f"route `{endpoint.__name__}` paths must start with '/'")

        if not inspect.isfunction(endpoint):
            raise ValueError(f"Endpoint `{endpoint}` must be a async function")

        self.path = path
        self.endpoint = endpoint
        self.name = u.get_endpoint_name(endpoint) if name is None else name
        self.include_in_schema = include_in_schema

        if methods is None:
            self.methods = {"GET", "HEAD"}
        else:
            methods = set([method.upper() for method in methods])
            if "GET" in methods:
                methods.add("HEAD")
            self.methods = methods

        self.path_regex, self.path_format, self.param_convertors = compile_path(path)

        # load app_label as tags
        if not tags:
            if app_label:
                tags = [app_label]
        self.tags = tags or []
        self.response_models = response_models

        self.app_label = app_label
        self.endpoint_definition = EndPointDefinition(
            endpoint=endpoint,
            methods=self.methods,
            tags=tags or [],
            path_parm_names=self.param_convertors.keys(),
            response_models=response_models,
        )

        self.app = EndpointHandler(self.endpoint_definition)

        self.load_middlewares(middleware)

    def load_middlewares(
        self, middlewares: t.Sequence[t.Type[MiddleWareProtocol]]
    ) -> None:
        if middlewares is not None:
            for cls in reversed(middlewares):
                self.app = cls(app=self.app)

    def update_path(self, new_path: str) -> None:
        self.path = new_path
        self.path_regex, self.path_format, self.param_convertors = compile_path(
            new_path
        )

        self.endpoint_definition = EndPointDefinition(
            endpoint=self.endpoint,
            methods=list(self.methods),
            tags=self.tags,
            path_parm_names=self.param_convertors.keys(),
            response_models=self.response_models,
        )

    def update_label(self, app_label: str) -> None:
        self.app_label = app_label
        if not self.tags:
            self.tags = [app_label]
