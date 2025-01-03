import typing as t

import pytest
from pydantic import BaseModel

from unfazed.http import HttpRequest, JsonResponse
from unfazed.openapi import OpenApi
from unfazed.route import Route, params
from unfazed.route.params import ResponseSpec
from unfazed.schema import OpenAPI, Server


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
    route = Route("/endpoint1", endpoint=endpoint1, tags=["tag1"])
    route2 = Route("/endpoint2", endpoint=endpoint2, tags=["tag1", "tag2"])

    ret = OpenApi.create_openapi_model(
        [route, route2],
        project_name="myproject",
        version="1.0.0",
        openapi_setting=OpenAPI(
            servers=[Server(url="http://localhost:8000", description="dev")]
        ),
    )

    # version
    assert ret.openapi == "3.1.0"

    # info
    assert ret.info.title == "myproject"
    assert ret.info.version == "1.0.0"

    # servers
    assert ret.servers is not None
    assert len(ret.servers) == 1
    assert ret.servers[0].url == "http://localhost:8000"
    assert ret.servers[0].description == "dev"

    # paths
    assert ret.paths is not None
    assert len(ret.paths) == 2
    assert "/endpoint1" in ret.paths
    pathitem = ret.paths["/endpoint1"]

    assert pathitem.post is None
    assert pathitem.get is not None

    parameters = pathitem.get.parameters
    assert parameters is not None

    params = [p.name for p in parameters]  # type: ignore
    assert "token" in params
    assert "token2" in params
    assert "token3" in params

    request_body = pathitem.get.requestBody

    assert request_body is not None
    assert "application/json" in request_body.content  # type: ignore

    responses = pathitem.get.responses

    assert "200" in responses

    response = responses["200"]
    assert response.content is not None
    content = response.content["application/json"]

    assert content.schema_ is not None
    assert content.schema_.ref is not None

    # test create schema result type
    schema = OpenApi.create_schema(
        [route, route2],
        project_name="myproject",
        version="1.0.0",
        openapi_setting=OpenAPI(
            servers=[Server(url="http://localhost:8000", description="dev")]
        ),
    )

    assert isinstance(schema, dict)

    # no openapi settings
    with pytest.raises(ValueError):
        OpenApi.create_openapi_model(
            [route, route2],
            project_name="myproject",
            version="1.0.0",
        )

    # include_in_schema
    route3 = Route(
        "/endpoint3", endpoint=endpoint1, tags=["tag1"], include_in_schema=False
    )
    ret = OpenApi.create_openapi_model(
        [route3],
        project_name="myproject",
        version="1.0.0",
        openapi_setting=OpenAPI(
            servers=[Server(url="http://localhost:8000", description="dev")]
        ),
    )

    assert ret.paths is not None
    assert len(ret.paths.keys()) == 0
