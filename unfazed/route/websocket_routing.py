import inspect
import typing as t

from pydantic import BaseModel, ConfigDict, create_model
from starlette.routing import WebSocketRoute as StarletteWebSocketRoute
from starlette.routing import compile_path
from starlette.websockets import WebSocketDisconnect, WebSocketState

from unfazed.http.websocket_connection import WebSocketConnection
from unfazed.protocol import MiddleWare as MiddleWareProtocol
from unfazed.type import CanBeImported, Receive, Scope, Send
from unfazed.utils import import_string

from . import params as p
from . import utils as u


class WebSocketEndpointDefinition(BaseModel):
    """Parse WebSocket endpoint signature and extract path/query params.

    Simplified version of EndPointDefinition for WebSocket endpoints.
    Only resolves path params (from URL pattern) and query params
    (from initial HTTP upgrade request query string).
    """

    endpoint: t.Callable
    path_parm_names: t.List[str]

    # stage 1: convert signature
    params: t.Dict[str, inspect.Parameter] | None = None

    # stage 2: dispatch
    path_params: t.Dict[str, t.Tuple[t.Type, p.Path]] = {}
    query_params: t.Dict[str, t.Type] = {}

    # stage 3: create model for path params (for validation)
    path_model: t.Type[BaseModel] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data: t.Any) -> None:
        super().__init__(**data)
        self.handle_signature()
        self.dispatch_params()
        self.build_path_model()

    def handle_signature(self) -> None:
        endpoint = self.endpoint
        type_hints = t.get_type_hints(endpoint, include_extras=True)
        signature = inspect.signature(endpoint)

        ret: t.Dict[str, inspect.Parameter] = {}
        for args, param in signature.parameters.items():
            if param.kind in [
                inspect.Parameter.VAR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            ]:
                continue

            # skip WebSocketConnection (first param)
            mro = getattr(param.annotation, "__mro__", [])
            if WebSocketConnection in mro:
                continue

            if param.name not in type_hints:
                raise TypeError(
                    f"missing type hint for '{param.name}' "
                    f"in endpoint: {self.endpoint_name}"
                )

            ret[args] = param

        self.params = ret

    def dispatch_params(self) -> None:
        self.params = self.params or {}
        for _, param in self.params.items():
            annotation = param.annotation

            # handle Annotated[type, Path()] pattern
            if hasattr(annotation, "_name") and annotation._name == "Annotated":
                metadata = annotation.__metadata__
                origin = annotation.__origin__
                model_or_field = metadata[0]

                if isinstance(model_or_field, p.Path):
                    self.path_params[param.name] = (origin, model_or_field)
                else:
                    raise ValueError(
                        f"Unsupported annotation for '{param.name}' "
                        f"in WebSocket endpoint: {self.endpoint_name}"
                    )
            else:
                # Plain type annotation without Annotated
                if param.name in self.path_parm_names:
                    self.path_params[param.name] = (annotation, p.Path())
                else:
                    self.query_params[param.name] = annotation

    def build_path_model(self) -> None:
        self.path_model = self._create_model(
            self.path_params,
            f"{self.endpoint.__name__.capitalize()}WSPathModel",
        )

    def _create_model(
        self,
        params: t.Mapping[str, t.Tuple[t.Type, "p.Param"]],
        model_name: str,
    ) -> t.Type[BaseModel] | None:
        if not params:
            return None

        field_definitions: t.Dict[str, t.Any] = {}
        for name, define in params.items():
            annotation, fieldinfo = define
            if not fieldinfo.alias:
                fieldinfo.alias = name
            if not fieldinfo.title:
                fieldinfo.title = name
            field_definitions[name] = (annotation, fieldinfo)

        return create_model(
            model_name,
            __config__=ConfigDict(arbitrary_types_allowed=True),
            **field_definitions,
        )

    @property
    def endpoint_name(self) -> str:
        return f"{self.endpoint.__module__}.{self.endpoint.__name__}"


class WebSocketEndpointHandler:
    """Layer 1 — Transport-level connection cleanup.

    Responsible for:
    1. Creating WebSocketConnection from ASGI scope
    2. Resolving path params and query params
    3. Calling the user's endpoint
    4. Ensuring clean WebSocket close on unexpected exceptions

    Call stack (inner to outer):
        WebSocketEndpointHandler.__call__           ← Layer 1: connection cleanup
            ↑ re-raises exceptions
        route-level middleware (load_middlewares)
            ↑
        global middleware stack (CommonMiddleware, etc.)  ← Layer 2: observation
            ↑
        Unfazed.__call__
    """

    def __init__(self, endpoint_definition: WebSocketEndpointDefinition) -> None:
        self.endpoint = endpoint_definition.endpoint
        self.endpoint_definition = endpoint_definition

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        ws = WebSocketConnection(scope, receive, send)
        kwargs = self._resolve_params(ws, scope)

        try:
            await self.endpoint(ws, **kwargs)

        except WebSocketDisconnect:
            # Client disconnected — not an error, exit silently.
            return  # pragma: no cover

        except Exception:
            # Ensure clean close on unexpected errors.
            # application_state can be:
            #   CONNECTING  — accept() not yet called, client awaits accept/close
            #   CONNECTED   — accept() called, actively exchanging messages
            #   DISCONNECTED — user already called ws.close(), skip
            if ws.application_state != WebSocketState.DISCONNECTED:
                try:
                    await ws.close(code=1011, reason="Internal server error")
                except Exception:  # pragma: no cover
                    pass
            raise

    def _resolve_params(
        self, ws: WebSocketConnection, scope: Scope
    ) -> t.Dict[str, t.Any]:
        kwargs: t.Dict[str, t.Any] = {}

        # Path params — Starlette already converted types via compile_path converters
        path_params = scope.get("path_params", {})
        for name in self.endpoint_definition.path_params:
            if name in path_params:
                kwargs[name] = path_params[name]

        # Query params — from initial HTTP upgrade request query string
        for name, annotation in self.endpoint_definition.query_params.items():
            raw = ws.query_params.get(name)
            if raw is not None:
                kwargs[name] = annotation(raw)

        return kwargs


class WebSocketRoute(StarletteWebSocketRoute):
    """
    WebSocket route for the Unfazed framework.

    Extends Starlette's WebSocketRoute with unfazed-specific features:
    - Path parameter resolution via WebSocketEndpointDefinition
    - Query parameter resolution from the initial HTTP upgrade request
    - Middleware support (same onion model as HTTP Route)
    - App label and tag support for organization
    """

    def __init__(
        self,
        path: str,
        endpoint: t.Callable[..., t.Any],
        *,
        name: str | None = None,
        middlewares: t.List[CanBeImported] | None = None,
        app_label: str | None = None,
        tags: t.List[str] | None = None,
    ) -> None:
        if not path.startswith("/"):
            raise ValueError(
                f"WebSocket route `{endpoint.__name__}` paths must start with '/'"
            )

        if not inspect.isfunction(endpoint):
            raise ValueError(f"WebSocket endpoint `{endpoint}` must be a function")

        self.path = path
        self.endpoint = endpoint
        self.name = u.get_endpoint_name(endpoint) if name is None else name
        self.include_in_schema = False

        self.path_regex, self.path_format, self.param_convertors = compile_path(path)

        if not tags:
            if app_label:
                tags = [app_label]
        self.tags = tags or []
        self.app_label = app_label

        self.endpoint_definition = WebSocketEndpointDefinition(
            endpoint=endpoint,
            path_parm_names=list(self.param_convertors.keys()),
        )

        self._middleware_strings = middlewares or []
        self.app = WebSocketEndpointHandler(self.endpoint_definition)
        self.load_middlewares(self._middleware_strings)

    def load_middlewares(self, middlewares: t.List[CanBeImported]) -> None:
        for cls_string in reversed(middlewares):
            cls: t.Type[MiddleWareProtocol] = import_string(cls_string)
            self.app = cls(app=self.app)

    def update_path(self, new_path: str) -> None:
        self.path = new_path
        original_param_keys = list(self.param_convertors.keys())
        self.path_regex, self.path_format, self.param_convertors = compile_path(
            new_path
        )
        if original_param_keys != list(self.param_convertors.keys()):
            self.endpoint_definition = WebSocketEndpointDefinition(
                endpoint=self.endpoint,
                path_parm_names=list(self.param_convertors.keys()),
            )
            self.app = WebSocketEndpointHandler(self.endpoint_definition)
            self.load_middlewares(self._middleware_strings)

    def update_label(self, app_label: str) -> None:
        self.app_label = app_label
        if not self.tags:
            self.tags = [app_label]
