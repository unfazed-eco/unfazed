import inspect
import typing as t

from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope
from pydantic import BaseModel, ConfigDict, Field, create_model
from pydantic.fields import FieldInfo
from starlette.concurrency import run_in_threadpool
from starlette.middleware import Middleware
from starlette.routing import Route as StartletteRoute
from starlette.routing import compile_path

from unfazed.http import HttpRequest
from unfazed.protocol import MiddleWare as MiddleWareProtocol
from unfazed.type import HttpMethod

from . import params as p
from . import utils as u

SUPPOTED_REQUEST_TYPE = t.Union[str, int, float, t.List, BaseModel]


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
            raise ValueError(f"Endpoint `{endpoint.__name__}` must be a async function")

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
            for cls, args, kwargs in reversed(middlewares):
                self.app = cls(app=self.app, *args, **kwargs)

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


class EndpointHandler:
    def __init__(self, endpoint_difinition: "EndPointDefinition") -> None:
        self.endpoint = endpoint_difinition.endpoint
        self.endpoint_difinition = endpoint_difinition

    async def __call__(
        self, scope: HTTPScope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> t.Any:
        request = HttpRequest(scope, receive, send)

        kwargs, error_list = await self.solve_params(request)

        if error_list:
            raise ExceptionGroup(
                f"failed to solve params for {self.endpoint_difinition.endpoint_name}",
                error_list,
            )

        if inspect.iscoroutinefunction(self.endpoint):
            response = await self.endpoint(request, **kwargs)
        else:
            response = await run_in_threadpool(self.endpoint, request, **kwargs)

        await response(scope, receive, send)

    async def solve_params(
        self, request: HttpRequest
    ) -> t.Tuple[t.Dict[str, t.Any], t.List[Exception]]:
        params: t.Dict[str, t.Any] = {}
        error_list: t.List[Exception] = []
        if self.endpoint_difinition.path_model:
            path_params, path_err = self._slove_path_params(request)
            params.update(path_params)
            if path_err:
                error_list.append(path_err)

        if self.endpoint_difinition.query_model:
            query_params, query_err = self._slove_query_params(request)
            params.update(query_params)
            if query_err:
                error_list.append(query_err)

        if self.endpoint_difinition.header_model:
            header_params, header_err = self._slove_header_params(request)
            params.update(header_params)
            if header_err:
                error_list.append(header_err)

        if self.endpoint_difinition.cookie_model:
            cookie_params, cookie_err = self._slove_cookie_params(request)
            params.update(cookie_params)
            if cookie_err:
                error_list.append(cookie_err)

        if self.endpoint_difinition.body_model:
            if self.endpoint_difinition.body_type == "json":
                body_params, body_err = self._slove_body_params(request)
                params.update(body_params)
                if body_err:
                    error_list.append(body_err)

            # handle formdata
            else:
                form_params, form_err = await self._slove_form_params(request)
                params.update(form_params)
                if form_err:
                    error_list.append(form_err)

        return params, error_list

    def _solve_params(
        self,
        model_cls: BaseModel,
        endpoint_params: t.Dict[str, t.Tuple[t.Type, BaseModel | FieldInfo]],
        request_params: t.Dict[str, t.Any],
    ) -> t.Tuple[t.Dict[str, t.Any], t.List[Exception]]:
        ret: t.Dict[str, t.Any] = {}
        ret_err: Exception | None = None

        # validate
        try:
            model_cls(**request_params)
        except Exception as err:
            ret_err = err

        for name, definition in endpoint_params.items():
            annotation = definition[0]

            if issubclass(annotation, BaseModel):
                ret[name] = annotation(**request_params)

            else:
                if name in request_params:
                    ret[name] = request_params[name]

        return ret, ret_err

    def _slove_path_params(
        self, request: HttpRequest
    ) -> t.Tuple[t.Dict[str, t.Any], Exception | None]:
        return self._solve_params(
            self.endpoint_difinition.path_model,
            self.endpoint_difinition.path_params,
            request.path_params,
        )

    def _slove_query_params(
        self, request: HttpRequest
    ) -> t.Tuple[t.Dict[str, t.Any], Exception | None]:
        return self._solve_params(
            self.endpoint_difinition.query_model,
            self.endpoint_difinition.query_params,
            request.query_params,
        )

    def _slove_header_params(
        self, request: HttpRequest
    ) -> t.Tuple[t.Dict[str, t.Any], Exception | None]:
        return self._solve_params(
            self.endpoint_difinition.header_model,
            self.endpoint_difinition.header_params,
            request.headers,
        )

    def _slove_cookie_params(
        self, request: HttpRequest
    ) -> t.Tuple[t.Dict[str, t.Any], Exception | None]:
        return self._solve_params(
            self.endpoint_difinition.cookie_model,
            self.endpoint_difinition.cookie_params,
            request.cookies,
        )

    def _slove_body_params(
        self, request: HttpRequest
    ) -> t.Tuple[t.Dict[str, t.Any], Exception | None]:
        return self._solve_params(
            self.endpoint_difinition.body_model,
            self.endpoint_difinition.body_params,
            request.json(),
        )

    async def _slove_form_params(self, request: HttpRequest):
        return self._solve_params(
            self.endpoint_difinition.body_model,
            self.endpoint_difinition.body_params,
            await request._get_form(),
        )


class EndPointDefinition(BaseModel):
    endpoint: t.Callable
    methods: t.List[str]
    tags: t.List[str]
    path_parm_names: t.List[str]

    # stage 1: convert signature to params and response
    params: t.Optional[t.Dict[str, inspect.Parameter]] = None
    response_models: t.Optional[t.List[p.ResponseSpec]] = None

    # stage 2: dispatch params to path, query, header, cookie, body params
    path_params: t.Dict[str, t.Tuple[t.Type, p.Path]] = {}
    query_params: t.Dict[str, t.Tuple[t.Type, p.Query]] = {}
    header_params: t.Dict[str, t.Tuple[t.Type, p.Header]] = {}
    cookie_params: t.Dict[str, t.Tuple[t.Type, p.Cookie]] = {}
    body_params: t.Dict[str, t.Tuple[t.Type, p.Body | p.Form | p.File]] = {}

    body_type: t.Optional[t.Literal["json", "form"]] = None

    # stage 3: create path, query, header, cookie, body models
    path_model: t.Type[BaseModel] | None = None
    query_model: t.Type[BaseModel] | None = None
    header_model: t.Type[BaseModel] | None = None
    cookie_model: t.Type[BaseModel] | None = None
    body_model: t.Type[BaseModel] | None = None

    operation_id: t.Optional[str] = Field(default_factory=u.generate_random_string)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        # stage 1
        self.handle_methods()
        self.handle_signature()
        # stage 2
        self.dispatch_params()
        # stage 3
        self.build_models()

    def _convert_args_to_params(self) -> t.Dict[str, inspect.Parameter]:
        endpoint = self.endpoint
        type_hints = t.get_type_hints(endpoint, include_extras=True)

        signature = inspect.signature(endpoint)

        # handle endpoint params
        ret: t.Dict[str, inspect.Parameter] = {}
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

            # raise if no type hint
            if param.name not in type_hints:
                raise ValueError(
                    f"missing type hint for {param.name} in endpoint: {self.endpoint_name}"
                )

            if param.default != inspect.Parameter.empty:
                raise ValueError(
                    f"endpoint {self.endpoint_name} should not have default value, use Annotated instead"
                    "change `{param.name}: {param.annotation} = {param.default}` "
                    "to `{param.name}: Annotated[{param.annotation}, Field(default={param.default})]`"
                )

            if (
                hasattr(param.annotation, "_name")
                and param.annotation._name == "Annotated"
            ):
                origin_cls = param.annotation.__origin__
            else:
                origin_cls = param.annotation
            if not issubclass(origin_cls, SUPPOTED_REQUEST_TYPE):
                raise ValueError(
                    f"unsupported type hint for `{param.name}` in endpoint: {self.endpoint.__name__}"
                    "supported types are: str, int, float, list, BaseModel"
                )

            ret[args] = param

        self.params = ret

    def _convert_return_to_response(self):
        endpoint = self.endpoint
        type_hints = t.get_type_hints(endpoint, include_extras=True)
        if "return" not in type_hints:
            raise ValueError(
                f"missing type hint for return in endpoint: {self.endpoint_name}"
            )

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
            response_models = []
            for model in _dict["__metadata__"]:
                if isinstance(model, p.ResponseSpec):
                    response_models.append(model)

            self.response_models = response_models

    def handle_signature(self):
        self._convert_args_to_params()
        self._convert_return_to_response()

    def dispatch_params(self):
        has_body_field = False
        has_form_field = False
        for _, param in self.params.items():
            annotation = param.annotation

            # async def endpoint(request: Request, q: str, path: int, ctx: Item) -> Response
            if not hasattr(annotation, "_name"):
                if param.name in self.path_parm_names:
                    self.path_params[param.name] = (annotation, p.Path())

                else:
                    if isinstance(annotation, t.Type) and issubclass(
                        annotation, BaseModel
                    ):
                        if has_form_field:
                            raise ValueError(
                                f"Error for {self.endpoint_name}: Cannot set body field and form field at the same time"
                            )
                        self.body_params[param.name] = (annotation, p.Body())
                        has_body_field = True
                    else:
                        self.query_params[param.name] = (annotation, p.Query())

            # async def endpoint(request: Request, ctx: t.Annotated[PathModel, p.Path()]) -> Response
            elif annotation._name == "Annotated":
                metadata = annotation.__metadata__
                origin = annotation.__origin__

                if not metadata:
                    raise ValueError(
                        f"{self.endpoint_name} missing metadata for {annotation}"
                    )

                # only support the first metadata
                model_or_field = metadata[0]

                if isinstance(model_or_field, p.Path):
                    self.path_params[param.name] = (origin, model_or_field)

                elif isinstance(model_or_field, p.Query):
                    self.query_params[param.name] = (origin, model_or_field)

                elif isinstance(model_or_field, p.Header):
                    self.header_params[param.name] = (origin, model_or_field)

                elif isinstance(model_or_field, p.Cookie):
                    self.cookie_params[param.name] = (origin, model_or_field)

                elif isinstance(model_or_field, p.Body):
                    if has_form_field:
                        raise ValueError(
                            f"Error for {self.endpoint_name}: Cannot set body field and form field at the same time"
                        )
                    self.body_params[param.name] = (origin, model_or_field)
                    has_body_field = True

                elif isinstance(model_or_field, p.Form):
                    if has_body_field:
                        raise ValueError(
                            f"Error for {self.endpoint_name}: Cannot set body field and form field at the same time"
                        )
                    self.body_params[param.name] = (origin, model_or_field)
                    has_form_field = True

                elif isinstance(model_or_field, p.File):
                    self.body_params[param.name] = (origin, model_or_field)

                else:
                    raise ValueError(
                        f"Unsupported Annotation for {param.name} in {self.endpoint_name}"
                    )

            else:
                raise ValueError(
                    f"Unsupported type hints for {param.name} in {self.endpoint_name}"
                )
        if has_body_field:
            self.body_type = "json"
        if has_form_field:
            self.body_type = "form"

    def handle_methods(self):
        # for openapi
        if "HEAD" in self.methods:
            self.methods.remove("HEAD")

    @property
    def endpoint_name(self) -> str:
        return f"{self.endpoint.__module__}.{self.endpoint.__name__}"

    def build_models(self):
        self.path_model = self.create_param_model(
            self.path_params,
            f"{self.endpoint.__name__.capitalize()}PathModel",
            "path",
            "simple",
        )

        self.query_model = self.create_param_model(
            self.query_params,
            f"{self.endpoint.__name__.capitalize()}QueryModel",
            "query",
            "form",
        )

        self.header_model = self.create_param_model(
            self.header_params,
            f"{self.endpoint.__name__.capitalize()}HeaderModel",
            "header",
            "simple",
        )

        self.cookie_model = self.create_param_model(
            self.cookie_params,
            f"{self.endpoint.__name__.capitalize()}CookieModel",
            "cookie",
            "form",
        )

        self.body_model = self.create_param_model(
            self.body_params, f"{self.endpoint.__name__.capitalize()}BodyModel"
        )

    @property
    def param_models(self) -> t.List[BaseModel | None]:
        return [
            self.path_model,
            self.query_model,
            self.header_model,
            self.cookie_model,
        ]

    def create_param_model(
        self,
        params: t.Dict[str, t.Tuple[t.Type, p.Param]],
        model_name: str,
        in_: str | None = None,
        style_: str | None = None,
    ) -> t.Type[BaseModel] | None:
        if not params:
            return None

        json_schema_extra = {}
        if in_:
            json_schema_extra["in_"] = in_
        if style_:
            json_schema_extra["style_"] = style_

        fields: t.List[str] = []
        bases: t.List[BaseModel] = []
        field_difinitions: t.Dict[str, p.Param] = {}

        for name, define in params.items():
            annotation: t.Type
            fieldinfo: p.Param

            annotation, fieldinfo = define

            if issubclass(annotation, BaseModel):
                for field_name, field in annotation.model_fields.items():
                    if field_name in fields:
                        raise ValueError(f"field {field_name} already exists")

                    fields.append(field_name)

                    if not field.alias:
                        field.alias = field_name

                    if not field.title:
                        field.title = field_name

                bases.append(annotation)

                if hasattr(field, "media_type"):
                    json_schema_extra["media_type"] = fieldinfo.media_type

            # field info
            else:
                if name in fields:
                    raise ValueError(
                        f"Error for {self.endpoint_name}: field {name} already exists"
                    )

                fields.append(name)

                if not fieldinfo.alias:
                    fieldinfo.alias = name

                if not fieldinfo.title:
                    fieldinfo.title = name

                field_difinitions[name] = define

        config_dict = ConfigDict()
        for base in bases:
            config_dict.update(base.model_config)

        if "json_schema_extra" in config_dict:
            config_dict["json_schema_extra"].update(json_schema_extra)
        else:
            config_dict["json_schema_extra"] = json_schema_extra

        field_difinitions["model_config"] = config_dict
        return create_model(
            model_name,
            __base__=tuple(bases) or None,
            **field_difinitions,
        )
