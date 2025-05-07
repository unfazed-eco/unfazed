import typing as t

import pytest
from openapi_pydantic.v3 import v3_0 as s
from pydantic import BaseModel

from unfazed.http import HttpRequest, JsonResponse
from unfazed.openapi import OpenApi
from unfazed.route import Route, params
from unfazed.route.params import ResponseSpec
from unfazed.schema import OpenAPI


class Fixed(BaseModel):
    foo: str


class Ctx(BaseModel):
    page: int
    size: int
    search: str
    fixed: Fixed = Fixed(foo="bar")


class Hdr(BaseModel):
    token: str
    token2: str
    token3: str


class Body1(BaseModel):
    name: str
    age: int


class Resp(BaseModel):
    message: str
    ctx: Ctx = Ctx(page=1, size=10, search="hello")


async def endpoint1(
    request: HttpRequest, ctx: Ctx, hdr: t.Annotated[Hdr, params.Header()]
) -> t.Annotated[JsonResponse, ResponseSpec(model=Resp)]:
    data = Resp(message="Hello, World!")
    return JsonResponse(data)


async def endpoint2(
    request: HttpRequest, ctx: Body1
) -> t.Annotated[JsonResponse, ResponseSpec(model=Resp)]:
    data = Resp(message="Hello, World!")
    return JsonResponse(data)


def test_openapi_create() -> None:
    route = Route(
        "/endpoint1",
        endpoint=endpoint1,
        tags=["tag1"],
        methods=["POST"],
        summary="endpoint1 summary",
        description="endpoint1 description",
        externalDocs={"url": "http://example.com", "description": "example"},
        operation_id="endpoint1_operation",
    )
    route2 = Route("/endpoint2", endpoint=endpoint2, tags=["tag1", "tag2"])

    openapi_setting = OpenAPI.model_validate(
        {
            "servers": [{"url": "http://localhost:8000", "description": "dev"}],
            "info": {
                "title": "myproject",
                "description": "desc",
                "termsOfService": "terms",
                "contact": {"name": "contact"},
                "license": {"name": "license"},
                "version": "1.0.0",
            },
        }
    )

    ret = OpenApi.create_openapi_model(
        [route, route2],
        openapi_setting=openapi_setting,
    )

    # version
    assert ret.openapi == "3.0.4"

    # info
    assert ret.info.title == "myproject"
    assert ret.info.version == "1.0.0"
    assert ret.info.description == "desc"
    assert ret.info.termsOfService == "terms"
    assert ret.info.contact is not None
    assert ret.info.contact.name == "contact"
    assert ret.info.license is not None
    assert ret.info.license.name == "license"

    # servers
    assert ret.servers is not None
    assert len(ret.servers) == 1
    assert ret.servers[0].url == "http://localhost:8000"
    assert ret.servers[0].description == "dev"

    # paths
    assert ret.paths is not None
    assert len(ret.paths) == 2

    # endpoint1
    assert "/endpoint1" in ret.paths
    pathitem = ret.paths["/endpoint1"]

    assert pathitem.post is not None
    assert pathitem.get is None
    assert pathitem.post.operationId == "endpoint1_operation"

    # parameters
    parameters = pathitem.post.parameters
    assert parameters is not None

    params = [p.name for p in parameters]  # type: ignore
    assert "token" in params
    assert "token2" in params
    assert "token3" in params

    # request body
    request_body = pathitem.post.requestBody

    assert request_body is not None
    assert "application/json" in request_body.content  # type: ignore
    media = request_body.content["application/json"]  # type: ignore

    assert media.media_type_schema is not None
    assert isinstance(media.media_type_schema, s.Reference)
    assert media.media_type_schema.ref is not None

    request_ref = media.media_type_schema.ref
    request_component = request_ref.split("/")[-1]

    # responses
    responses = pathitem.post.responses

    assert "200" in responses

    response = responses["200"]
    assert isinstance(response, s.Response)
    assert response.content is not None
    content = response.content["application/json"]

    assert content.media_type_schema is not None
    assert isinstance(content.media_type_schema, s.Reference)

    assert content.media_type_schema.ref is not None

    response_200_ref = content.media_type_schema.ref
    response_200_component = response_200_ref.split("/")[-1]

    # components
    assert ret.components is not None
    assert ret.components.schemas is not None

    assert request_component in ret.components.schemas
    assert response_200_component in ret.components.schemas

    # test create schema result type
    schema = OpenApi.create_schema(
        [route, route2],
        openapi_setting=OpenAPI.model_validate(
            {
                "servers": [{"url": "http://localhost:8000", "description": "dev"}],
                "info": {
                    "title": "myproject",
                    "version": "1.0.0",
                    "description": "desc",
                },
            }
        ),
    )

    assert isinstance(schema, dict)

    # no openapi settings
    with pytest.raises(ValueError):
        OpenApi.create_openapi_model(
            [route, route2],
        )

    # include_in_schema
    route3 = Route(
        "/endpoint3", endpoint=endpoint1, tags=["tag1"], include_in_schema=False
    )
    ret = OpenApi.create_openapi_model(
        [route3],
        openapi_setting=OpenAPI.model_validate(
            {
                "servers": [{"url": "http://localhost:8000", "description": "dev"}],
                "info": {
                    "title": "myproject",
                    "version": "1.0.0",
                    "description": "desc",
                },
            }
        ),
    )

    assert ret.paths is not None
    assert len(ret.paths.keys()) == 0
