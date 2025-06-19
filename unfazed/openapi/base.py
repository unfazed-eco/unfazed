import typing as t

from openapi_pydantic.v3 import v3_1 as v3_1_spec
from pydantic import BaseModel

from unfazed.route import Route
from unfazed.route.params import Param, ResponseSpec
from unfazed.schema import OpenAPI as OpenAPISettingModel

s = v3_1_spec

REF = "#/components/schemas/"


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
    def get_reponse_schema_name(cls, route: Route, model_name: str) -> str:
        definition = route.endpoint_definition
        return f"{definition.endpoint_name}.{model_name}"

    @classmethod
    def create_pathitem_from_route(cls, route: Route) -> s.PathItem:
        definition = route.endpoint_definition

        # ----
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

                schema_name = fieldinfo.alias or name

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
                deprecated = json_schema_extra_dict.get("deprecated", False)
                allowEmptyValue = json_schema_extra_dict.get("allowEmptyValue", False)
                explode = json_schema_extra_dict.get("explode", None)
                allowReserved = json_schema_extra_dict.get("allowReserved", False)

                item = s.Parameter.model_validate(
                    {
                        "name": fieldinfo.alias or fieldinfo.title,
                        "in": json_schema_extra_dict["in_"],
                        "style": json_schema_extra_dict["style_"],
                        "required": fieldinfo.is_required(),
                        "schema": s.Schema.model_validate(
                            json_schema["properties"][schema_name]
                        ),
                        "description": fieldinfo.description,
                        "example": example,
                        "examples": examples,
                        "deprecated": deprecated,
                        "allowEmptyValue": allowEmptyValue,
                        "explode": explode,
                        "allowReserved": allowReserved,
                    }
                )
                parameters.append(item)

        # handle request body
        content: t.Dict[str, s.MediaType] = {}

        required = False
        request_body_desc: str | None = None
        if definition.body_model:
            bd_model: t.Type[BaseModel] = definition.body_model
            required = True
            bd_json_schema = bd_model.model_config.get("json_schema_extra", {})

            # comply with mypy check
            if not bd_json_schema or not isinstance(bd_json_schema, dict):
                bd_json_schema = {}  # pragma: no cover
            content_type = bd_json_schema.get("media_type")
            request_body_desc = t.cast(
                t.Union[str, None], bd_json_schema.get("description")
            )
            if not content_type or not isinstance(content_type, str):
                content_type = "application/json"  # pragma: no cover
            example = bd_json_schema.get("example")
            examples = bd_json_schema.get("examples")
            request_model_name = cls.get_reponse_schema_name(route, bd_model.__name__)
            media_type = s.MediaType(
                schema=s.Reference.model_validate({"$ref": REF + request_model_name}),
                examples=examples,  # type: ignore
                example=example,
            )
            content[content_type] = media_type

        request_body = s.RequestBody(
            required=required,
            content=content,
            description=request_body_desc,
        )

        # handle responses
        responses: t.Dict[str, t.Union[s.Response, s.Reference]] = {}
        response: ResponseSpec
        response_models = definition.response_models or []
        for response in response_models:
            resp_model = response.model
            resp_model_name = cls.get_reponse_schema_name(route, resp_model.__name__)
            rm_json_schema = resp_model.model_config.get("json_schema_extra", {})
            if not rm_json_schema or not isinstance(rm_json_schema, dict):
                rm_json_schema = {}
            example = rm_json_schema.get("example")
            examples = rm_json_schema.get("examples")

            media_type = s.MediaType(
                schema=s.Reference.model_validate({"$ref": REF + resp_model_name}),
                example=example,
                examples=examples,  # type: ignore
            )
            responses[response.code] = s.Response.model_validate(
                {
                    "description": response.description,
                    "headers": response.headers,
                    "content": {response.content_type: media_type},
                }
            )

        externalDocs = None
        if route.externalDocs:
            externalDocs = s.ExternalDocumentation.model_validate(route.externalDocs)
        operation = s.Operation(
            tags=[t.name for t in endpoint_tags],
            summary=route.summary,
            description=route.description,
            externalDocs=externalDocs,
            operationId=definition.operation_id,
            deprecated=route.deprecated,
            parameters=parameters,  # type: ignore
            requestBody=request_body,
            responses=responses,
        )

        method_map: t.Dict[str, s.Operation] = {}
        for method in definition.methods:
            method_map[method.lower()] = operation
        path_item = s.PathItem.model_validate(method_map)

        path_item.summary = route.summary
        path_item.description = route.description

        return path_item

    @classmethod
    def create_schema_from_route_resp_model(cls, route: Route) -> t.Dict[str, t.Any]:
        definition = route.endpoint_definition

        schemas: t.Dict[str, t.Any] = {}

        response: ResponseSpec
        response_models = definition.response_models or []
        for response in response_models:
            response_schema = response.model.model_json_schema(
                ref_template=REF + route.endpoint_definition.endpoint_name + ".{model}"
            )

            if "$defs" in response_schema:
                nested_model_schema = response_schema.pop("$defs")
                for model_name, model_schema in nested_model_schema.items():
                    schema_model_name = cls.get_reponse_schema_name(route, model_name)
                    schemas[schema_model_name] = model_schema

            resp_model_name = cls.get_reponse_schema_name(
                route, response.model.__name__
            )
            schemas[resp_model_name] = response_schema

        return schemas

    @classmethod
    def create_schema_from_route_request_model(cls, route: Route) -> t.Dict[str, t.Any]:
        definition = route.endpoint_definition

        schemas: t.Dict[str, t.Any] = {}

        if definition.body_model:
            bd_model: t.Type[BaseModel] = definition.body_model
            bd_json_schema = bd_model.model_json_schema(
                ref_template=REF + route.endpoint_definition.endpoint_name + ".{model}"
            )

            if "$defs" in bd_json_schema:
                nested_model_schema = bd_json_schema.pop("$defs")
                for model_name, model_schema in nested_model_schema.items():
                    schema_model_name = cls.get_reponse_schema_name(route, model_name)
                    schemas[schema_model_name] = model_schema

            resp_model_name = cls.get_reponse_schema_name(route, bd_model.__name__)
            schemas[resp_model_name] = bd_json_schema

        return schemas

    @classmethod
    def create_openapi_model(
        cls,
        routes: t.List[Route],
        openapi_setting: OpenAPISettingModel | None = None,
    ) -> s.OpenAPI:
        if not openapi_setting:
            raise ValueError("OpenAPI settings not found")

        openapi_basic_fields = {
            "paths": {},
            **openapi_setting.model_dump(
                exclude={"allow_public", "json_route", "swagger_ui", "redoc"}
            ),
        }

        ret = s.OpenAPI.model_validate(openapi_basic_fields)

        paths: t.Dict[str, t.Any] = {}
        schemas: t.Dict[str, t.Any] = {}
        tags: t.Dict[str, s.Tag] = {}

        for route in routes:
            if not route.include_in_schema:
                continue

            cls.create_tags_from_route(route, tags)
            temp_resp_schemas = cls.create_schema_from_route_resp_model(route)
            temp_req_schemas = cls.create_schema_from_route_request_model(route)
            pathitem = cls.create_pathitem_from_route(route)
            paths[route.path] = pathitem
            schemas.update(temp_resp_schemas)
            schemas.update(temp_req_schemas)

        components: s.Components = s.Components(schemas=schemas)
        ret.components = components
        ret.tags = list(tags.values())
        ret.paths = paths

        return ret

    @classmethod
    def create_schema(
        cls,
        routes: t.List[Route],
        openapi_setting: OpenAPISettingModel | None = None,
    ) -> t.Dict:
        ret = cls.create_openapi_model(routes, openapi_setting)
        cls.schema = ret.model_dump(by_alias=True, exclude_none=True, mode="json")

        return cls.schema
