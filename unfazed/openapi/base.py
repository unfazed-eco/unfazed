import typing as t

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from unfazed.conf import UnfazedSettings, settings
from unfazed.route import Route
from unfazed.route.params import ResponseSpec

from . import spec as s

REF = "#/components/schemas/"
DEFAULT_REF_TPL = REF + "{model}"


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
            if route.include_in_schema is False:
                continue

            definition = route.endpoint_definition

            # handle openapi tags
            endpoint_tags = definition.tags

            for name in endpoint_tags:
                if name not in tags:
                    tags[name] = s.Tag(name=name)

            # ----
            endpoint_name = definition.endpoint_name

            parameters = []

            for _model in definition.param_models:
                if not _model:
                    continue
                model: BaseModel = _model
                json_schema = model.model_json_schema()
                for name in model.model_fields:
                    fieldinfo: FieldInfo = model.model_fields[name]
                    item = s.Parameter(
                        **{
                            "in": model.model_config.json_schema_extra["in_"],
                            "style": fieldinfo.json_schema_extra["style_"],
                            "name": fieldinfo.alias or fieldinfo.title,
                            "required": fieldinfo.is_required(),
                            "schema_": s.Schema(**json_schema["properties"][name]),
                            "description": fieldinfo.description,
                        }
                    )
                    parameters.append(item)

            # handle content
            content: t.Dict[str, s.MediaType] = {}

            required = False
            if definition.body_model:
                required = True
                # TODO
                # handle formdata currently only handle json
                content_type = "applicaiton/json"
                body_schema = definition.body_model.model_json_schema(
                    ref_template=DEFAULT_REF_TPL
                )
                media_type = s.MediaType(schema=body_schema)
                content[content_type] = media_type

            request_body = s.RequestBody(
                required=required,
                content=content,
                description=f"request for {endpoint_name}",
            )

            responses: t.Dict[str, s.Response] = {}

            for response in definition.response_models:
                response: ResponseSpec
                response_schema = response.model.model_json_schema(
                    ref_template=DEFAULT_REF_TPL
                )
                responses[response.code] = s.Response(
                    description=response.description,
                    content={
                        response.content_type: s.MediaType(schema=response_schema)
                    },
                )

            description = (
                definition.endpoint.__doc__
                or f"endpoint for {definition.endpoint_name}"
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

            # TODO
            # decide only support one method for one route
            for method in definition.methods:
                path_item = s.PathItem(**{method: operation})
                paths[route.path] = path_item

        components: t.Dict[str, t.Any] = {"schemas": schemas}
        ret.components = components  # type: ignore
        ret.tags = list(tags.values())
        ret.paths = paths

        cls.schema = ret.model_json_schema(by_alias=True)

        return cls.schema
