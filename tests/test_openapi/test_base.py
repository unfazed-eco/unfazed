import typing as t

from pydantic import BaseModel

from unfazed.http import HttpRequest, JsonResponse
from unfazed.openapi import OpenApi
from unfazed.route import Route, params
from unfazed.route.params import ResponseSpec
from unfazed.schema import OpenAPI


class Ctx(BaseModel):
    page: int
    size: int
    search: str


class Hdr(BaseModel):
    token: str
    token2: str
    token3: str


class Body1(BaseModel):
    name: str
    age: int


class Resp(BaseModel):
    message: str
    ctx: Ctx


async def endpoint1(
    request: HttpRequest, ctx: Ctx, hdr: t.Annotated[Hdr, params.Header()]
) -> t.Annotated[JsonResponse[Resp], ResponseSpec(model=Resp)]:
    data = Resp(message="Hello, World!")
    return JsonResponse(data)


async def endpoint2(
    request: HttpRequest, ctx: Body1
) -> t.Annotated[JsonResponse[Resp], ResponseSpec(model=Resp)]:
    data = Resp(message="Hello, World!")
    return JsonResponse(data)


def test_openapi_create() -> None:
    route = Route("/endpoint1", endpoint=endpoint1, tags=["tag1"])
    route2 = Route("/endpoint2", endpoint=endpoint2, tags=["tag1", "tag2"])

    ret = OpenApi.create_openapi_model(
        [route, route2],
        project_name="myproject",
        version="1.0.0",
        openapi_setting=OpenAPI(
            servers=[{"url": "http://localhost:8000", "description": "dev"}]
        ),
    )

    # version
    assert ret.openapi == "3.1.0"

    # info
    assert ret.info.title == "myproject"
    assert ret.info.version == "1.0.0"

    # servers
    assert len(ret.servers) == 1
    assert ret.servers[0].url == "http://localhost:8000"
    assert ret.servers[0].description == "dev"

    # paths
    assert len(ret.paths) == 2
    assert "/endpoint1" in ret.paths
    pathitem = ret.paths["/endpoint1"]

    assert pathitem.post is None
    assert pathitem.get is not None

    parameters = pathitem.get.parameters

    params = [p.name for p in parameters]
    assert "token" in params
    assert "token2" in params
    assert "token3" in params

    request_body = pathitem.get.requestBody

    assert request_body is not None
    assert "application/json" in request_body.content

    responses = pathitem.get.responses

    assert "200" in responses

    response = responses["200"]
    content = response.content["application/json"]

    assert content.schema_.ref is not None

    # test create schema result type
    schema = OpenApi.create_schema(
        [route, route2],
        project_name="myproject",
        version="1.0.0",
        openapi_setting=OpenAPI(
            servers=[{"url": "http://localhost:8000", "description": "dev"}]
        ),
    )

    assert isinstance(schema, dict)

    # no openapi settings
    ret = OpenApi.create_openapi_model(
        [route, route2],
        project_name="myproject",
        version="1.0.0",
    )

    assert ret is None

    # include_in_schema
    route3 = Route(
        "/endpoint3", endpoint=endpoint1, tags=["tag1"], include_in_schema=False
    )
    ret = OpenApi.create_openapi_model(
        [route3],
        project_name="myproject",
        version="1.0.0",
        openapi_setting=OpenAPI(
            servers=[{"url": "http://localhost:8000", "description": "dev"}]
        ),
    )

    assert len(ret.paths) == 0
