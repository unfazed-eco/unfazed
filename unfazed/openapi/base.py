import inspect
import typing as t
from itertools import chain

from pydantic import BaseModel, ConfigDict, Field
from pydantic.fields import FieldInfo

from unfazed.conf import UnfazedSettings, settings
from unfazed.http import HttpRequest, HttpResponse
from unfazed.route import Route

from . import params as p
from . import spec as s
from . import utils as u
from .spec import Tag


class RouteInfo(BaseModel):
    endpoint: t.Callable
    methods: t.List[str]

    tags: t.List[Tag]
    path_parm_names: t.List[str]  # route.path_conventers.keys()

    params: t.Optional[t.Dict[str, inspect.Parameter]] = None
    # content_type: t.Optional[str] = None
    path_params: t.List[p.Path | p.PathField] = []
    query_params: t.List[p.Query | p.QueryField] = []
    header_params: t.List[p.Header | p.HeaderField] = []
    cookie_params: t.List[p.Cookie | p.CookieField] = []
    body_params: t.List[p.Body | p.BodyField] = []
    # body_field: t.Optional[FieldInfo] = None
    response_models: t.Optional[t.List[BaseModel]] = None
    operation_id: t.Optional[str] = Field(default_factory=u._generate_random_string)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.handle_methods()
        self.get_param_annotation()
        self.analyze()

    def handle_methods(self):
        if "HEAD" in self.methods:
            self.methods.remove("HEAD")

    def flaten_params(
        self, params: t.List[p.Param | BaseModel], in_: str, style_: str = "simple"
    ) -> t.List[FieldInfo]:
        ret: t.List[FieldInfo] = []
        for param in params:
            if isinstance(param, p.Param):
                ret.append(param)
            elif isinstance(param, BaseModel):
                for field in param.model_fields.values():
                    field.in_ = in_
                    field.style_ = style_
                    ret.append(field)
            else:
                raise ValueError(f"unsupported param: {param}")

        return ret

    @property
    def iter_params(self):
        return chain(
            self.flaten_params(self.path_params, in_="path"),
            self.flaten_params(self.query_params, in_="query"),
            self.flaten_params(self.header_params, in_="header"),
            self.flaten_params(self.cookie_params, in_="cookie"),
            self.flaten_params(self.body_params, in_="body"),
        )

    def get_param_annotation(self):
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
                if not isinstance(model, s.Response):
                    raise ValueError(f"unsupported metadata: {model}")

            self.response_models = _dict["__metadata__"]

    def analyze(self):
        for _, param in self.params.items():
            annotation = param.annotation
            default = param.default

            # TODO
            # 特定的参数类型才能被作为 endpoint 的参数

            # args: str/int
            if not hasattr(annotation, "_name"):
                if param.name in self.path_parm_names:
                    default = p.PathField()
                    self.path_params.append(default)
                elif default == inspect.Parameter.empty:
                    if isinstance(annotation, t.Type) and issubclass(
                        annotation, BaseModel
                    ):
                        default = p.Body()
                        self.body_params.append(default)
                    else:
                        default = p.Query()
                        self.query_params.append(default)
                else:
                    raise ValueError(f"unsupported type: {annotation}")

            # args: t.Annotated[PathModel, p.Path()]
            elif annotation._name == "Annotated":
                metadata = annotation.__metadata__

                if not metadata:
                    raise ValueError(f"missing metadata for {annotation}")

                # only support the first metadata
                # TODO
                # support formfiled and filefield
                match metadata[0]:
                    case p.Path():
                        self.path_params.append(metadata[0])
                    case p.Query():
                        self.query_params.append(metadata[0])
                    case p.Header():
                        self.header_params.append(metadata[0])
                    case p.Cookie():
                        self.cookie_params.append(metadata[0])
                    case p.Body():
                        self.body_params.append(metadata[0])
                    case p.PathField():
                        self.path_params.append(metadata[0])
                    case p.QueryField():
                        self.query_params.append(metadata[0])
                    case p.HeaderField():
                        self.header_params.append(metadata[0])
                    case p.CookieField():
                        self.cookie_params.append(metadata[0])
                    case p.BodyField():
                        self.body_params.append(metadata[0])
                    case _:
                        raise ValueError(f"unsupported metadata: {metadata}")

            else:
                raise ValueError(f"unknown param type: {default}")


class OpenApi:
    schema: t.Dict[str, t.Any] | None = None

    @classmethod
    def create_schema(cls, routes: t.List[Route]) -> t.Dict:
        unfazedsettings: UnfazedSettings = settings["UNFAZED_SETTINGS"]

        if not unfazedsettings.OPENAPI:
            return

        info = s.Info(
            title=unfazedsettings.PROJECT_NAME,
            unfazedsettings=settings.VERSION,
        )
        ret = s.OpenAPI(info=info, servers=unfazedsettings.OPENAPI.servers)

        paths: t.Dict[str, t.Any] = {}
        schemas: t.Dict[str, t.Any] = {}
        tags: t.Dict[str, s.Tag] = {}

        for route in routes:
            if route.ignore:
                continue

            route_info = RouteInfo(
                endpoint=route.endpoint,
                method=route.methods[0],
                tags=[Tag(name=tag) for tag in route.tags],
                path_parm_names=route.param_convertors.keys(),
                response_models=route.responses,
            )

            # handle openapi tags
            endpoint_tags = route_info.tags

            for tag in endpoint_tags:
                if tag.name not in tags:
                    tags[tag.name] = tag

            # ----
            func_name = route.endpoint.__name__

            parameters = []

            for param in route_info.iter_params:
                item = s.Parameter(
                    **{
                        "in": param.in_,  # set in flaten_params
                        "style": param.style_,  # set in flaten_params
                        "name": param.alias or param.title,
                        "required": param.is_required(),
                        "schema_": s.Schema(**u._generate_field_schema(param)),
                        "description": param.description,
                    }
                )
                parameters.append(item)

            content: t.Dict[str, s.MediaType] = {}
            request_body = s.RequestBody(
                required=False,
                content=content,
                description=f"request for {func_name}",
            )

            responses: t.Dict[str, s.Response] = {}
            res_models = []

            for model in res_models:
                pass

            description = route_info.endpoint.__doc__ or f"endpoint for {func_name}"

            operation = s.Operation(
                summary=func_name,
                tags=[t.name for t in endpoint_tags],
                parameters=parameters,
                description=description,
                operationId=route_info.operation_id,
                requestBody=request_body,
                responses=responses,
            )

            # TODO
            # decide only support one method for one route
            for method in route_info.methods:
                path_item = s.PathItem(**{method: operation})
                paths[route.path] = path_item

        components: t.Dict[str, t.Any] = {"schemas": schemas}
        ret.components = components  # type: ignore
        ret.tags = list(tags.values())
        ret.paths = paths

        cls.schema = ret.model_dump(exclude_none=True, by_alias=True)

        return cls.schema
