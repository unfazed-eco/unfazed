import typing as t

from pydantic import BaseModel

from unfazed.route import Route
from unfazed.route.params import Param, ResponseSpec
from unfazed.schema import OpenAPI as OpenAPISettingModel

from . import spec as s

REF = "#/components/schemas/"
DEFAULT_REF_TPL = REF + "{model}"


class OpenApi:
    schema: t.Dict[str, t.Any] | None = None

    @classmethod
    def create_tags_from_route(cls, route: Route, tags: t.Dict[str, s.Tag]) -> None:
        definition = route.endpoint_definition

        # handle openapi tags
        endpoint_tags = definition.tags

        for name in endpoint_tags:
            if name not in tags:
                tags[name] = s.Tag(name=name)

    @classmethod
    def get_reponse_schema_name(cls, route: Route, response: ResponseSpec) -> str:
        definition = route.endpoint_definition
        return f"{definition.endpoint_name}.{response.model.__name__}.{response.code}"

    @classmethod
    def create_pathitem_from_route(cls, route: Route) -> s.PathItem:
        definition = route.endpoint_definition

        # ----
        endpoint_name = definition.endpoint_name
        endpoint_tags = [s.Tag(name=t) for t in definition.tags]

        # handle parameters
        parameters = []

        for _model in definition.param_models:
            if not _model:
                continue
            model: t.Type[BaseModel] = _model
            json_schema = model.model_json_schema()
            for name in model.model_fields:
                fieldinfo: Param = t.cast(Param, model.model_fields[name])
                # in / style / name
                # provided by EndPointDefinition._create_param_model
                json_schema_extra_dict = model.model_config.get("json_schema_extra")

                # comply with mypy check
                if not json_schema_extra_dict or not isinstance(
                    json_schema_extra_dict, dict
                ):
                    json_schema_extra_dict = {}  # pragma: no cover
                example = json_schema_extra_dict.get("example")
                examples = json_schema_extra_dict.get("examples")
                item = s.Parameter.model_validate(
                    {
                        "in": json_schema_extra_dict["in_"],
                        "style": json_schema_extra_dict["style_"],
                        "name": fieldinfo.alias or fieldinfo.title,
                        "required": fieldinfo.is_required(),
                        "schema_": s.Schema(**json_schema["properties"][name]),
                        "description": fieldinfo.description,
                        "example": example,
                        "examples": examples,
                    }
                )
                parameters.append(item)

        # handle request body
        content: t.Dict[str, s.MediaType] = {}

        required = False
        if definition.body_model:
            bd_model: t.Type[BaseModel] = definition.body_model
            required = True
            bd_json_schema = bd_model.model_config.get("json_schema_extra", {})

            # comply with mypy check
            if not bd_json_schema or not isinstance(bd_json_schema, dict):
                bd_json_schema = {}  # pragma: no cover
            content_type = bd_json_schema.get("media_type")
            if not content_type or not isinstance(content_type, str):
                content_type = "application/json"  # pragma: no cover
            example = bd_json_schema.get("example")
            examples = bd_json_schema.get("examples")
            body_schema = bd_model.model_json_schema(ref_template=DEFAULT_REF_TPL)
            media_type = s.MediaType(
                schema=s.Schema.model_validate(body_schema),
                examples=examples,  # type: ignore
                example=example,
            )
            content[content_type] = media_type

        request_body = s.RequestBody(
            required=required,
            content=content,
            description=f"Request Body for {endpoint_name}",
        )

        # handle responses
        responses: t.Dict[str, s.Response] = {}
        response: ResponseSpec
        response_models = definition.response_models or []
        for response in response_models:
            resp_model = response.model
            resp_model_name = cls.get_reponse_schema_name(route, response)
            rm_json_schema = resp_model.model_config.get("json_schema_extra", {})
            if not rm_json_schema or not isinstance(rm_json_schema, dict):
                rm_json_schema = {}
            example = rm_json_schema.get("example")
            examples = rm_json_schema.get("examples")

            media_type = s.MediaType(
                schema=s.Reference(ref=REF + resp_model_name),
                example=example,
                examples=examples,  # type: ignore
            )
            responses[response.code] = s.Response(
                description=response.description,
                content={response.content_type: media_type},
            )

        description = (
            definition.endpoint.__doc__ or f"endpoint for {definition.endpoint_name}"
        )

        operation = s.Operation(
            summary=definition.endpoint_name,
            tags=[t.name for t in endpoint_tags],
            parameters=parameters,  # type: ignore
            description=description,
            operationId=definition.operation_id,
            requestBody=request_body,
            responses=responses,
        )

        method_map: t.Dict[str, s.Operation] = {}
        for method in definition.methods:
            method_map[method.lower()] = operation
        path_item = s.PathItem.model_validate(method_map)

        return path_item

    @classmethod
    def create_schema_from_route_resp_model(cls, route: Route) -> t.Dict[str, t.Any]:
        definition = route.endpoint_definition

        schemas: t.Dict[str, t.Any] = {}

        response: ResponseSpec
        response_models = definition.response_models or []
        for response in response_models:
            response_schema = response.model.model_json_schema(
                ref_template=DEFAULT_REF_TPL
            )

            if "$defs" in response_schema:
                nested_model_schema = response_schema.pop("$defs")
                schemas.update(nested_model_schema)

            resp_model_name = cls.get_reponse_schema_name(route, response)
            schemas[resp_model_name] = response_schema

        return schemas

    @classmethod
    def create_openapi_model(
        cls,
        routes: t.List[Route],
        project_name: str,
        version: str,
        openapi_setting: OpenAPISettingModel | None = None,
    ) -> s.OpenAPI:
        if not openapi_setting:
            raise ValueError("OpenAPI settings not found")

        info = s.Info(
            title=project_name,
            version=version,
        )
        ret = s.OpenAPI(
            info=info,
            servers=[
                s.Server.model_validate(i.model_dump()) for i in openapi_setting.servers
            ],
        )

        paths: t.Dict[str, t.Any] = {}
        schemas: t.Dict[str, t.Any] = {}
        tags: t.Dict[str, s.Tag] = {}

        for route in routes:
            if not route.include_in_schema:
                continue

            cls.create_tags_from_route(route, tags)
            temp_schemas = cls.create_schema_from_route_resp_model(route)
            pathitem = cls.create_pathitem_from_route(route)
            paths[route.path] = pathitem
            schemas.update(temp_schemas)

        components: t.Dict[str, t.Any] = {"schemas": schemas}
        ret.components = components  # type: ignore
        ret.tags = list(tags.values())
        ret.paths = paths

        return ret

    @classmethod
    def create_schema(
        cls,
        routes: t.List[Route],
        project_name: str,
        version: str,
        openapi_setting: OpenAPISettingModel | None = None,
    ) -> t.Dict:
        ret = cls.create_openapi_model(routes, project_name, version, openapi_setting)
        cls.schema = ret.model_dump(by_alias=True, exclude_none=True)

        return cls.schema
