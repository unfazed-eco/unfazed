import inspect
import typing as t

from pydantic import BaseModel, ConfigDict, Field, create_model
from pydantic.fields import FieldInfo
from starlette.middleware import Middleware
from starlette.routing import Route as StartletteRoute
from starlette.routing import compile_path

from unfazed.http import HttpRequest, HttpResponse
from unfazed.protocol import MiddleWare as MiddleWareProtocol

from . import params as p
from . import utils as u

if t.TYPE_CHECKING:
    from unfazed.openapi.spec import Tag


class Route(StartletteRoute):
    def __init__(
        self,
        path: str,
        endpoint: t.Callable[..., t.Any],
        *,
        methods: list[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        middleware: t.Sequence[Middleware] | None = None,
        app_label: str | None = None,
        tags: t.List[str] | None = None,
        response_models: t.List[p.ResponseSpec] | None = None,
    ) -> None:
        super().__init__(
            path,
            endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
            middleware=middleware,
        )

        self.app_label = app_label

        self.route_detail = RouteDetail(
            endpoint=endpoint,
            methods=methods,
            tags=tags,
            path_parm_names=self.param_convertors.keys(),
            response_models=response_models,
        )

    def load_middlewares(
        self, middlewares: t.Sequence[t.Type[MiddleWareProtocol]]
    ) -> None:
        if middlewares is not None:
            for cls, args, kwargs in reversed(middlewares):
                self.app = cls(app=self.app, *args, **kwargs)

    def update_path(self, new_path: str) -> None:
        self.path_regex, self.path_format, self.param_convertors = compile_path(
            new_path
        )

        self.route_detail = RouteDetail(
            endpoint=self.endpoint,
            methods=self.methods,
            tags=self.tags,
            path_parm_names=self.param_convertors.keys(),
        )


class EndpointHandler:
    def __call__(self, *args: inspect.Any, **kwds: inspect.Any) -> inspect.Any:
        pass


class RouteDetail(BaseModel):
    endpoint: t.Callable
    methods: t.List[str]
    tags: t.List["Tag"]
    path_parm_names: t.List[str]

    params: t.Optional[t.Dict[str, inspect.Parameter]] = None
    path_params: t.Dict[str, t.Tuple[t.Type, p.Path | p.PathField]] = {}
    query_params: t.Dict[str, t.Tuple[t.Type, p.Query | p.QueryField]] = {}
    header_params: t.Dict[str, t.Tuple[t.Type, p.Header | p.HeaderField]] = {}
    cookie_params: t.Dict[str, t.Tuple[t.Type, p.Cookie | p.CookieField]] = {}
    body_params: t.Dict[str, t.Tuple[t.Type, p.Body | p.BodyField]] = {}
    response_models: t.Optional[t.List[BaseModel]] = None
    operation_id: t.Optional[str] = Field(default_factory=u._generate_random_string)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.handle_methods()
        self.fill_params()
        self.analyze()

    def handle_methods(self):
        if "HEAD" in self.methods:
            self.methods.remove("HEAD")

    @property
    def endpoint_name(self) -> str:
        return f"{self.endpoint.__module__}.{self.endpoint.__name__}"

    @property
    def path_model(self):
        return self.create_param_model(self.path_params, "PathModel")

    @property
    def query_model(self):
        return self.create_param_model(self.query_params, "QueryModel")

    @property
    def header_model(self):
        return self.create_param_model(self.header_params, "HeaderModel")

    @property
    def cookie_model(self):
        return self.create_param_model(self.cookie_params, "CookieModel")

    @property
    def body_model(self):
        if (
            self.body_params
            and len(self.body_params) == 1
            and isinstance(self.body_params[0], BaseModel)
        ):
            return self.body_params[0]

        return self.create_param_model(self.body_params, "BodyModel")

    def param_models(self) -> t.List[BaseModel | None]:
        return [
            self.path_model,
            self.query_model,
            self.header_model,
            self.cookie_model,
            self.body_model,
        ]

    def create_param_model(
        self,
        params: t.Dict[str, t.Tuple[t.Type, BaseModel | FieldInfo]],
        model_name: str,
    ) -> t.Type[BaseModel] | None:
        if not params:
            return None

        fields: t.List[str] = []
        bases: t.List[BaseModel] = []
        field_difinitions: t.Dict[str, FieldInfo] = {}

        for name, define in params.items():
            annotation = define[0]
            if issubclass(annotation, BaseModel):
                for field_name in annotation.model_fields:
                    if field_name in fields:
                        raise ValueError(f"field {field_name} already exists")

                    fields.append(field_name)

                bases.append(annotation)

            else:
                if name in fields:
                    raise ValueError(f"field {name} already exists")

                fields.append(name)

                field_difinitions[name] = define

        config_dict = ConfigDict()
        for base in bases:
            config_dict.update(base.model_config)

        return create_model(
            model_name,
            __base__=bases,
            __config__=config_dict,
            **params,
        )

    def fill_params(self):
        endpoint = self.endpoint
        type_hints = t.get_type_hints(endpoint, include_extras=True)

        signature = inspect.signature(endpoint)

        # handle endpoint params
        ret: t.Dict[str, t.Any] = {}
        for args, param in signature.parameters.items():
            if param.kind in [
                inspect.Parameter.VAR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            ]:
                continue

            # skip param `self`
            if param.name == "self":
                continue

            # skip unfazed request
            mro = getattr(param.annotation, "__mro__", [])
            if HttpRequest in mro:
                continue

            # raise if no typing hint
            if param.name not in type_hints:
                raise ValueError(f"missing type hint for {param.name}")

            ret[args] = param

        self.params = ret

        if "return" not in type_hints:
            raise ValueError(f"missing type hint for return in endpoint: {endpoint}")

        # if set response_models at path("/", response_model=yourmodels)
        # ignore return type
        if self.response_models:
            return

        # handle return type
        """
        suported return type:

            async def v1(request: HttpRequest) -> HttpResponse:
                return HttpResponse()

            async def v2(request: HttpRequest) -> Annotated[HttpResponse, meta1, meta2]:
                return HttpResponse()
        """

        _dict = type_hints["return"].__dict__

        # only support Annotated[HttpResponse, resp1, resp2]
        if "__origin__" in _dict and "__metadata__" in _dict:
            origin = _dict["__origin__"]
            if HttpResponse not in getattr(origin, "__mro__", []):
                raise ValueError(
                    f"return type in {endpoint.__name__} need inherited from HttpResponse"
                )

            for model in _dict["__metadata__"]:
                if not isinstance(model, ResponseSpec):
                    raise ValueError(f"unsupported metadata: {model}")

            self.response_models = _dict["__metadata__"]

    def analyze(self):
        for _, param in self.params.items():
            annotation = param.annotation
            default = param.default

            # TODO
            # 特定的参数类型才能被作为 endpoint 的参数

            # async def endpoint(request: Request, q: str, path: int, ctx: Item) -> Response
            if not hasattr(annotation, "_name"):
                if param.name in self.path_parm_names:
                    self.path_params[param.name] = p.PathField(default=default)
                elif default == inspect.Parameter.empty:
                    if isinstance(annotation, t.Type) and issubclass(
                        annotation, BaseModel
                    ):
                        self.body_params[param.name] = default
                    else:
                        self.query_params[param.name] = p.QueryField(default=default)
                else:
                    raise ValueError(f"unsupported type: {annotation}")

            # async def endpoint(request: Request, ctx: t.Annotated[PathModel, p.Path()]) -> Response
            elif annotation._name == "Annotated":
                metadata = annotation.__metadata__
                origin = annotation.__origin__

                if not metadata:
                    raise ValueError(f"missing metadata for {annotation}")

                # TODO
                # support formfiled and filefield

                # only support the first metadata
                model_or_field = metadata[0]

                if isinstance(model_or_field, p.Path):
                    if not issubclass(origin, BaseModel):
                        raise ValueError(
                            f"endpoint {self.endpoint_name} with wrong signature "
                            "for param {param.name}, it should be inherited by BaseModel"
                        )
                    self.path_params[param.name] = (origin, ...)

                elif isinstance(model_or_field, p.Query):
                    if not issubclass(origin, BaseModel):
                        raise ValueError(
                            f"endpoint {self.endpoint_name} with wrong signature "
                            "for param {param.name}, it should be inherited by BaseModel"
                        )

                    self.query_params[param.name] = (origin, ...)

                elif isinstance(model_or_field, p.Header):
                    if not issubclass(origin, BaseModel):
                        raise ValueError(
                            f"endpoint {self.endpoint_name} with wrong signature "
                            "for param {param.name}, it should be inherited by BaseModel"
                        )

                    self.header_params[param.name] = (origin, ...)

                elif isinstance(model_or_field, p.Cookie):
                    if not issubclass(origin, BaseModel):
                        raise ValueError(
                            f"endpoint {self.endpoint_name} with wrong signature "
                            "for param {param.name}, it should be inherited by BaseModel"
                        )

                    self.cookie_params[param.name] = (origin, ...)

                elif isinstance(model_or_field, p.Body):
                    if not issubclass(origin, BaseModel):
                        raise ValueError(
                            f"endpoint {self.endpoint_name} with wrong signature "
                            "for param {param.name}, it should be inherited by BaseModel"
                        )

                    self.body_params[param.name] = (origin, ...)

                elif isinstance(model_or_field, p.PathField):
                    self.path_params[param.name] = (annotation, model_or_field)

                elif isinstance(model_or_field, p.QueryField):
                    self.query_params[param.name] = (annotation, model_or_field)

                elif isinstance(model_or_field, p.HeaderField):
                    self.query_params[param.name] = (annotation, model_or_field)

                elif isinstance(model_or_field, p.CookieField):
                    self.cookie_params[param.name] = (annotation, model_or_field)

                elif isinstance(model_or_field, p.BodyField):
                    self.body_params[param.name] = (annotation, model_or_field)

                else:
                    raise ValueError(
                        f"Unsupported Annotation for {param.name} in {self.endpoint_name}"
                    )

            else:
                raise ValueError(
                    f"Unsupported type hints for {param.name} in {self.endpoint_name}"
                )
