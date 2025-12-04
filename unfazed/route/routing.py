import inspect
import typing as t

from starlette.routing import Match, Router, URLPath, compile_path, get_route_path
from starlette.routing import Route as StartletteRoute

from unfazed.protocol import MiddleWare as MiddleWareProtocol
from unfazed.static import StaticFiles
from unfazed.type import ASGIApp, CanBeImported, HttpMethod, Receive, Scope, Send
from unfazed.utils import import_string

from . import params as p
from . import utils as u
from .endpoint import EndPointDefinition, EndpointHandler

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class Route(StartletteRoute):
    @t.override
    def __init__(
        self,
        path: str,
        endpoint: t.Callable[..., t.Any],
        *,
        methods: t.List[HttpMethod] | None = None,
        name: str | None = None,
        middlewares: t.List[CanBeImported] | None = None,
        app_label: str | None = None,
        tags: t.List[str] | None = None,
        include_in_schema: bool = True,
        summary: str | None = None,
        description: str | None = None,
        externalDocs: t.Dict | None = None,
        deprecated: bool | None = None,
        operation_id: str | None = None,
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
        self.summary = summary
        self.description = description
        self.externalDocs = externalDocs
        self.deprecated = deprecated or False
        self.operation_id = operation_id

        if methods is None:
            methods_set = {"GET", "HEAD"}
        else:
            methods_set = {method.upper() for method in methods}
            if "GET" in methods_set:
                methods_set.add("HEAD")
        self.methods = methods_set

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

        if operation_id:
            self.endpoint_definition.operation_id = operation_id

        self.app = EndpointHandler(self.endpoint_definition)

        self.load_middlewares(middlewares or [])

    def load_middlewares(self, middlewares: t.List[CanBeImported]) -> None:
        for cls_string in reversed(middlewares):
            cls: t.Type[MiddleWareProtocol] = import_string(cls_string)
            self.app = cls(app=self.app)

    def update_path(self, new_path: str) -> None:
        self.path = new_path
        self.path_regex, self.path_format, self.param_convertors = compile_path(
            new_path
        )

        self.endpoint_definition = EndPointDefinition(
            endpoint=self.endpoint,
            methods=self.methods,
            tags=self.tags,
            path_parm_names=self.param_convertors.keys(),
            response_models=self.response_models,
        )

        if self.operation_id:
            self.endpoint_definition.operation_id = self.operation_id

    def update_label(self, app_label: str) -> None:
        self.app_label = app_label
        if not self.tags:
            self.tags = [app_label]


class Static(Route):
    @t.override
    def __init__(
        self,
        path: str,
        directory: str,
        *,
        name: str | None = None,
        middlewares: t.List[CanBeImported] | None = None,
        html: bool = False,
        app_label: str | None = None,
    ) -> None:
        if not path.startswith("/"):
            raise ValueError(f"route `{path}` must start with '/'")

        path = path.rstrip("/")

        self.path = path
        self.directory = directory
        self.name = name or "static"

        self.methods = {"GET", "HEAD"}
        self.path_regex, self.path_format, self.param_convertors = compile_path(
            path + "/{path:path}"
        )
        self.app: StaticFiles = StaticFiles(directory=directory, html=html)

        self.load_middlewares(middlewares or [])

        self.app_label = app_label

        self.include_in_schema = False

    @t.override
    def url_path_for(self, name: str, /, **path_params: t.Any) -> URLPath:
        raise NotImplementedError("Static routes not support yet")  # type: ignore

    @t.override
    def matches(self, scope: Scope) -> t.Tuple[Match, Scope]:
        path_params: dict[str, t.Any]
        if scope["type"] == "http":
            root_path = scope.get("root_path", "")
            route_path = get_route_path(scope)
            match = self.path_regex.match(route_path)
            if not match and route_path.strip("/") == self.path.strip("/"):
                match = self.path_regex.match(route_path + "/")
            if match:
                matched_params = match.groupdict()
                for key, value in matched_params.items():
                    matched_params[key] = self.param_convertors[key].convert(value)

                remaining_path = "/" + matched_params.pop("path")
                matched_path = route_path[: -len(remaining_path)]
                path_params = dict(scope.get("path_params", {}))
                path_params.update(matched_params)
                child_scope = {
                    "path_params": path_params,
                    "root_path": root_path + matched_path,
                    "endpoint": self.app,
                }

                return Match.FULL, child_scope
        return Match.NONE, {}

    @t.override
    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        return await self.app(scope, receive, send)

    @property
    def routes(self) -> t.List[Route]:
        return []

    def update_label(self, app_label: str) -> None:
        self.app_label = app_label


class Mount(Route):
    @t.override
    def __init__(
        self,
        path: str,
        app: ASGIApp | None = None,
        routes: t.List[Route] | None = None,
        *,
        name: str | None = None,
        app_label: str | None = None,
        middlewares: t.List[CanBeImported] | None = None,
    ) -> None:
        if not path.startswith("/"):
            raise ValueError(f"route `{path}` must start with '/'")

        self.path = path.rstrip("/")

        need_setup = False

        if app is not None:
            self.app = app
            from unfazed.core import Unfazed

            if isinstance(app, Unfazed):
                need_setup = True
        elif routes is not None:
            self.app = Router(routes)
        else:
            raise ValueError("Mount must have either an app or routes")

        self.need_setup = need_setup

        self.load_middlewares(middlewares or [])
        self.app_label = app_label

        self.name = name or ""
        self.path_regex, self.path_format, self.param_convertors = compile_path(
            self.path + "/{path:path}"
        )

        self.include_in_schema = False

    @property
    def routes(self) -> t.List[Route]:
        return getattr(self.app, "routes", [])

    @t.override
    def url_path_for(self, name: str, /, **path_params: t.Any) -> URLPath:
        raise NotImplementedError("Mount routes not support yet")  # type: ignore

    @t.override
    def matches(self, scope: Scope) -> t.Tuple[Match, Scope]:
        # from starlette.routing.Mount.matches
        path_params: t.Dict[str, t.Any]
        if scope["type"] in ("http", "websocket"):
            root_path = scope.get("root_path", "")
            route_path = get_route_path(scope)
            match = self.path_regex.match(route_path)
            if match:
                matched_params = match.groupdict()
                for key, value in matched_params.items():
                    matched_params[key] = self.param_convertors[key].convert(value)
                remaining_path = "/" + matched_params.pop("path")
                matched_path = route_path[: -len(remaining_path)]
                path_params = dict(scope.get("path_params", {}))
                path_params.update(matched_params)
                child_scope = {
                    "path_params": path_params,
                    "app_root_path": scope.get("app_root_path", root_path),
                    "root_path": root_path + matched_path,
                    "endpoint": self.app,
                }
                return Match.FULL, child_scope
        return Match.NONE, {}

    @t.override
    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.need_setup:
            unfazed_app = t.cast("Unfazed", self.app)
            await unfazed_app.setup()
            self.need_setup = False
        return await self.app(scope, receive, send)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Mount)
            and self.path == other.path
            and self.app == other.app
        )

    def __repr__(self) -> str:
        name = self.name or ""
        return f"Mount(path={self.path!r}, name={name!r}, app={self.app!r})"

    def update_label(self, app_label: str) -> None:
        self.app_label = app_label
