import inspect
import typing as t

from pydantic import BaseModel, ConfigDict, Field, WithJsonSchema, create_model
from starlette.concurrency import run_in_threadpool

from unfazed.exception import ParameterError, TypeHintRequired
from unfazed.file import UploadFile
from unfazed.http import HttpRequest
from unfazed.type import Receive, Scope, Send

from . import params as p
from . import utils as u

SUPPOTED_REQUEST_TYPE = (str, int, float, t.List, BaseModel, UploadFile)


class EndpointHandler:
    """
    A wrapper class that handles parameter resolution for endpoint functions.

    This class transforms a simple endpoint function signature:
    ```python
    async def endpoint(request: HttpRequest) -> Response
    ```

    Into a more detailed signature with typed parameters:
    ```python
    async def endpoint(
        request: HttpRequest,
        ctx: t.Annotated[PathModel, p.Path()],      # Path parameters
        q: t.Annotated[QueryModel, p.Query()],      # Query parameters
        h: t.Annotated[HeaderModel, p.Header()],    # Header parameters
        c: t.Annotated[CookieModel, p.Cookie()],    # Cookie parameters
        b: t.Annotated[JsonModel, p.Json()]         # JSON body parameters
    ) -> Response
    ```

    The handler automatically resolves and validates parameters from different sources
    (path, query, headers, cookies, and request body) based on their annotations.
    """

    def __init__(self, endpoint_definition: "EndPointDefinition") -> None:
        self.endpoint = endpoint_definition.endpoint
        self.endpoint_definition = endpoint_definition

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = HttpRequest(scope, receive, send)

        kwargs, error_list = await self.solve_params(request)

        if error_list:
            raise ExceptionGroup(
                f"failed to solve params for {self.endpoint_definition.endpoint_name}",
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
        if self.endpoint_definition.path_model:
            path_params, path_err = self._solve_params(
                self.endpoint_definition.path_model,
                self.endpoint_definition.path_params,
                request.path_params,
            )
            params.update(path_params)
            if path_err:
                error_list.append(path_err)

        if self.endpoint_definition.query_model:
            query_params, query_err = self._solve_params(
                self.endpoint_definition.query_model,
                self.endpoint_definition.query_params,
                t.cast(t.Dict[str, t.Any], request.query_params),
            )
            params.update(query_params)
            if query_err:
                error_list.append(query_err)

        if self.endpoint_definition.header_model:
            header_params, header_err = self._solve_params(
                self.endpoint_definition.header_model,
                self.endpoint_definition.header_params,
                t.cast(t.Dict[str, t.Any], request.headers),
            )
            params.update(header_params)
            if header_err:
                error_list.append(header_err)

        if self.endpoint_definition.cookie_model:
            cookie_params, cookie_err = self._solve_params(
                self.endpoint_definition.cookie_model,
                self.endpoint_definition.cookie_params,
                t.cast(t.Dict[str, t.Any], request.cookies),
            )
            params.update(cookie_params)
            if cookie_err:
                error_list.append(cookie_err)

        if self.endpoint_definition.body_model:
            if self.endpoint_definition.body_type == "json":
                body_params, body_err = self._solve_params(
                    self.endpoint_definition.body_model,
                    self.endpoint_definition.body_params,
                    t.cast(t.Dict[str, t.Any], await request.json()),
                )
                params.update(body_params)
                if body_err:
                    error_list.append(body_err)

            # handle formdata
            else:
                form_params, form_err = self._solve_params(
                    self.endpoint_definition.body_model,
                    self.endpoint_definition.body_params,
                    t.cast(t.Dict[str, t.Any], await request.form()),
                )
                params.update(form_params)
                if form_err:
                    error_list.append(form_err)

        return params, error_list

    def _solve_params(
        self,
        model_cls: t.Type[BaseModel],
        endpoint_params: t.Mapping[str, t.Tuple[t.Type, p.Param]],
        request_params: t.Mapping[str, t.Any],
    ) -> t.Tuple[t.Dict[str, t.Any], Exception | None]:
        ret: t.Dict[str, t.Any] = {}
        ret_err: Exception | None = None

        # validate
        try:
            model_cls.model_validate(request_params)
        except Exception as err:
            ret_err = ParameterError(str(err))

        if ret_err:
            return ret, ret_err

        for name, definition in endpoint_params.items():
            annotation, fieldinfo = definition

            # create default value
            if fieldinfo.default is not None:
                ret[name] = fieldinfo.default

            # override default value if request has value
            if issubclass(annotation, BaseModel):
                ret[name] = annotation(**request_params)

            else:
                if name in request_params:
                    ret[name] = request_params[name]

        return ret, ret_err


class EndPointDefinition(BaseModel):
    """
    Parse endpoint signature and create models for path, query, header, cookie, body

    Stages:
        1. init endpointDefinition with endpoint/method/tags/path_parm_names
        2. convert signature to *_params and response
        3. dispatch params to path, query, header, cookie, body params
        4. create path, query, header, cookie, body models from each type of params

    """

    endpoint: t.Callable
    methods: t.Set[str]
    tags: t.List[str]
    path_parm_names: t.List[str]

    # stage 1: convert signature to params and response
    params: t.Dict[str, inspect.Parameter] | None = None
    response_models: t.List[p.ResponseSpec] | None = None

    # stage 2: dispatch params to path, query, header, cookie, body params
    path_params: t.Dict[str, t.Tuple[t.Type, p.Path]] = {}
    query_params: t.Dict[str, t.Tuple[t.Type, p.Query]] = {}
    header_params: t.Dict[str, t.Tuple[t.Type, p.Header]] = {}
    cookie_params: t.Dict[str, t.Tuple[t.Type, p.Cookie]] = {}
    body_params: t.Dict[str, t.Tuple[t.Type, p.Json | p.Form | p.File]] = {}

    body_type: t.Optional[t.Literal["json", "form"]] = None

    # stage 3: create path, query, header, cookie, body models
    path_model: t.Type[BaseModel] | None = None
    query_model: t.Type[BaseModel] | None = None
    header_model: t.Type[BaseModel] | None = None
    cookie_model: t.Type[BaseModel] | None = None
    body_model: t.Type[BaseModel] | None = None

    operation_id: t.Optional[str] = Field(default_factory=u.generate_random_string)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data: t.Any) -> None:
        super().__init__(**data)
        # stage 1
        self.handle_methods()
        self.handle_signature()
        # stage 2
        self.dispatch_params()
        # stage 3
        self.build_models()

    def _convert_args_to_params(self) -> None:
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

            # skip unfazed request
            mro = getattr(param.annotation, "__mro__", [])
            if HttpRequest in mro:
                continue

            # raise if no type hint
            if param.name not in type_hints:
                raise TypeHintRequired(
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

    def _convert_return_to_response(self) -> None:
        if self.response_models is None:
            self.response_models = []
        else:
            # if set response_models at path("/", response_models={yourmodels})
            # ignore return type
            return

        endpoint = self.endpoint
        type_hints = t.get_type_hints(endpoint, include_extras=True)
        if "return" not in type_hints:
            raise TypeHintRequired(
                f"missing type hint for return in endpoint: {self.endpoint_name}"
            )

        _dict = type_hints["return"].__dict__

        # only support Annotated[HttpResponse, resp1, resp2]
        if "__origin__" in _dict and "__metadata__" in _dict:
            response_models = []
            for model in _dict["__metadata__"]:
                if isinstance(model, p.ResponseSpec):
                    response_models.append(model)

            self.response_models = response_models

    def handle_signature(self) -> None:
        self._convert_args_to_params()
        self._convert_return_to_response()

    def dispatch_params(self) -> None:
        has_body_field = False
        has_form_field = False

        self.params = self.params or {}
        for _, param in self.params.items():
            annotation = param.annotation

            # async def endpoint(request: Request, ctx: t.Annotated[PathModel, p.Path()]) -> Response
            if hasattr(annotation, "_name") and annotation._name == "Annotated":
                metadata = annotation.__metadata__
                origin = annotation.__origin__

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

                elif isinstance(model_or_field, p.Json):
                    if has_form_field:
                        raise ValueError(
                            f"Error for {self.endpoint_name}: Cannot set json field and form field at the same time"
                        )
                    self.body_params[param.name] = (origin, model_or_field)
                    has_body_field = True

                elif isinstance(model_or_field, p.Form):
                    if has_body_field:
                        raise ValueError(
                            f"Error for {self.endpoint_name}: Cannot set json field and form field at the same time"
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
                # async def endpoint(request: Request, q: str, path: int, ctx: Item) -> Response
                if param.name in self.path_parm_names:
                    self.path_params[param.name] = (annotation, p.Path())

                else:
                    if issubclass(annotation, BaseModel):
                        if has_form_field:
                            raise ValueError(
                                f"Error for {self.endpoint_name}: Cannot set Json field and form field at the same time"
                            )
                        self.body_params[param.name] = (annotation, p.Json())
                        has_body_field = True
                    else:
                        self.query_params[param.name] = (annotation, p.Query())

        if has_body_field:
            self.body_type = "json"
        if has_form_field:
            self.body_type = "form"

    def handle_methods(self) -> None:
        # for openapi
        if "HEAD" in self.methods:
            self.methods.remove("HEAD")

    @property
    def endpoint_name(self) -> str:
        return f"{self.endpoint.__module__}.{self.endpoint.__name__}"

    def build_models(self) -> None:
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
    def param_models(self) -> t.List[t.Type[BaseModel] | None]:
        return [
            self.path_model,
            self.query_model,
            self.header_model,
            self.cookie_model,
        ]

    def create_param_model(
        self,
        params: t.Dict[str, t.Tuple[t.Type[BaseModel], t.Annotated[t.Any, "p.Param"]]],
        model_name: str,
        in_: str | None = None,
        style_: str | None = None,
    ) -> t.Type[BaseModel] | None:
        if not params:
            return None

        json_schema_extra: t.Dict[str, t.Any] = {}
        if in_:
            json_schema_extra["in_"] = in_
        if style_:
            json_schema_extra["style_"] = style_

        fields: t.List[str] = []
        bases: t.List[t.Type[BaseModel]] = []
        field_difinitions: t.Dict[str, t.Annotated[t.Any, "p.Parms"]] = {}

        for name, define in params.items():
            annotation: t.Type
            fieldinfo: p.Param

            annotation, fieldinfo = define

            # Uploadfile need special json schema
            if issubclass(annotation, UploadFile):
                new_json_schema_extra = {"type": "string", "format": "binary"}
                old_annotation = t.cast(UploadFile, annotation)
                annotation = t.Annotated[  # type: ignore
                    old_annotation, WithJsonSchema(new_json_schema_extra)
                ]

            if hasattr(fieldinfo, "media_type"):
                json_schema_extra["media_type"] = fieldinfo.media_type

            if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                for field_name, field in annotation.model_fields.items():
                    if field_name in fields:
                        raise ValueError(f"field {field_name} already exists")

                    fields.append(field_name)

                    if not field.alias:
                        field.alias = field_name

                    if not field.title:
                        field.title = field_name

                bases.append(annotation)

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

                field_difinitions[name] = (annotation, fieldinfo)

        # arbitrary_types_allowed = True for UploadFile
        config_dict = ConfigDict(arbitrary_types_allowed=True)
        for base in bases:
            config_dict.update(base.model_config)

        if "json_schema_extra" in config_dict and isinstance(
            config_dict["json_schema_extra"], t.Dict
        ):
            config_dict["json_schema_extra"].update(json_schema_extra)
        else:
            config_dict["json_schema_extra"] = json_schema_extra

        # field_difinitions["model_config"] = config_dict

        if bases:
            base_one = bases[0]
            base_one.model_config = config_dict

            model_cls = create_model(
                model_name,
                __base__=tuple(bases) or None,
                **field_difinitions,
            )
        else:
            model_cls = create_model(
                model_name,
                **field_difinitions,
                __config__=config_dict,
            )

        return model_cls
