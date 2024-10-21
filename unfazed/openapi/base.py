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
    def create_pathitem_from_route(cls, route: Route) -> t.Tuple[s.PathItem, t.Dict]:
        definition = route.endpoint_definition

        # ----
        endpoint_name = definition.endpoint_name
        endpoint_tags = [s.Tag(name=t) for t in definition.tags]

        # handle parameters
        parameters = []

        for _model in definition.param_models:
            if not _model:
                continue
            model: BaseModel = _model
            json_schema = model.model_json_schema()
            for name in model.model_fields:
                fieldinfo: Param = model.model_fields[name]
                # in / style / name
                # provided by EndPointDefinition._create_param_model
                json_schema_extra = model.model_config.get("json_schema_extra", {})
                example = json_schema_extra.get("example")
                examples = json_schema_extra.get("examples")
                item = s.Parameter(
                    **{
                        "in": json_schema_extra["in_"],
                        "style": json_schema_extra["style_"],
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
            model: BaseModel = definition.body_model
            required = True
            json_schema_extra = model.model_config.get("json_schema_extra", {})
            content_type = json_schema_extra.get("media_type", "application/json")

            example = json_schema_extra.get("example")
            examples = json_schema_extra.get("examples")
            body_schema = model.model_json_schema(ref_template=DEFAULT_REF_TPL)
            media_type = s.MediaType(
                schema=body_schema,
                examples=examples,
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

        for response in definition.response_models:
            response: ResponseSpec

            resp_model_name = cls.get_reponse_schema_name(route, response)
            json_schema_extra = model.model_config.get("json_schema_extra", {})
            example = json_schema_extra.get("example")
            examples = json_schema_extra.get("examples")

            media_type = s.MediaType(schema=s.Reference(ref=REF + resp_model_name))
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
            parameters=parameters,
            description=description,
            operationId=definition.operation_id,
            requestBody=request_body,
            responses=responses,
        )

        method_map: t.Dict[str, s.Operation] = {}
        for method in definition.methods:
            method_map[method.lower()] = operation
        path_item = s.PathItem(**method_map)

        return path_item

    @classmethod
    def create_schema_from_route_resp_model(cls, route: Route) -> t.Dict[str, t.Any]:
        definition = route.endpoint_definition

        schemas: t.Dict[str, t.Any] = {}

        for response in definition.response_models:
            response: ResponseSpec

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
            return

        info = s.Info(
            title=project_name,
            version=version,
        )
        ret = s.OpenAPI(
            info=info, servers=[i.model_dump() for i in openapi_setting.servers]
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
