import typing as t

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from unfazed.conf import UnfazedSettings, settings
from unfazed.route import Route

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

            route_details = route.route_detail

            # handle openapi tags
            endpoint_tags = route_details.tags

            for name in endpoint_tags:
                if name not in tags:
                    tags[name] = s.Tag(name=name)

            # ----
            endpoint_name = route_details.endpoint_name

            parameters = []

            for _model in route_details.param_models:
                if not _model:
                    continue
                model: BaseModel = _model
                json_schema = model.model_json_schema()
                for name in model.model_fields:
                    fieldinfo: FieldInfo = model.model_fields[name]
                    item = s.Parameter(
                        **{
                            "in": fieldinfo.json_schema_extra.get("in_", "query"),
                            "style": fieldinfo.json_schema_extra.get("style", "form"),
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
            if route_details.body_model:
                required = True
                # TODO
                # handle formdata currently only handle json
                content_type = "applicaiton/json"
                media_type = s.MediaType(schema=body_schema)
                content[content_type] = media_type

            request_body = s.RequestBody(
                required=required,
                content=content,
                description=f"request for {endpoint_name}",
            )

            responses: t.Dict[str, s.Response] = {}
            res_models = []

            for model in res_models:
                pass

            description = route_details.endpoint.__doc__ or f"endpoint for {func_name}"

            operation = s.Operation(
                summary=func_name,
                tags=[t.name for t in endpoint_tags],
                parameters=parameters,
                description=description,
                operationId=route_details.operation_id,
                requestBody=request_body,
                responses=responses,
            )

            # TODO
            # decide only support one method for one route
            for method in route_details.methods:
                path_item = s.PathItem(**{method: operation})
                paths[route.path] = path_item

        components: t.Dict[str, t.Any] = {"schemas": schemas}
        ret.components = components  # type: ignore
        ret.tags = list(tags.values())
        ret.paths = paths

        cls.schema = ret.model_dump(exclude_none=True, by_alias=True)

        return cls.schema
