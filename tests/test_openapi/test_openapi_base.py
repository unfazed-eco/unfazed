import typing as t
from enum import StrEnum

import pytest
from openapi_pydantic.v3 import v3_1 as s
from pydantic import BaseModel, Field

from unfazed.file import UploadFile
from unfazed.http import HttpRequest, JsonResponse
from unfazed.openapi import OpenApi
from unfazed.route import Route, params
from unfazed.route.params import ResponseSpec
from unfazed.schema import OpenAPI


class IdRequest(BaseModel):
    id: int = Field(..., description="ID")


class Enum1(StrEnum):
    A = "a"
    B = "b"
    C = "c"


class Pth(BaseModel):
    pth1: str
    pth2: str = Field(..., description="pth2")


class Qry(BaseModel):
    qry1: str
    qry2: str = Field(..., description="qry2")


class Jsn(BaseModel):
    jsn1: str
    jsn2: str = Field(..., description="jsn2")


class Hdr(BaseModel):
    hdr1: str
    hdr2: str = Field(..., description="hdr2")

    # issue 42
    hdr3: str = Field(..., description="hdr3", alias="hdr3-alias")


class Ckie(BaseModel):
    ckie1: str
    ckie2: str = Field(..., description="ckie2")


class Frm(BaseModel):
    frm1: str
    frm2: str = Field(..., description="frm2")


class Jsn2(BaseModel):
    jsn21: Jsn
    jsn22: str = Field(..., description="jsn22")
    jsn23: Enum1 = Field(..., description="jsn23")
    jsn24: t.Optional[str] = Field(default=None, description="jsn24")
    jsn25: t.Optional[IdRequest] = Field(default=None, description="jsn25")


class Resp(BaseModel):
    message: str


class Resp2(BaseModel):
    resp: Resp
    code: int


async def endpoint1(
    request: HttpRequest,
    pth: t.Annotated[Pth, params.Path()],
) -> t.Annotated[JsonResponse, ResponseSpec(model=Resp)]:
    return JsonResponse(Resp(message="hello"))


async def endpoint2(
    request: HttpRequest,
    hdr: t.Annotated[Hdr, params.Header()],
    ckie: t.Annotated[Ckie, params.Cookie()],
    jsn: t.Annotated[Jsn, params.Json()],
) -> t.Annotated[JsonResponse, ResponseSpec(model=Resp)]:
    return JsonResponse(Resp(message="hello"))


async def endpoint3(
    request: HttpRequest,
    frm: t.Annotated[Frm, params.Form()],
    file1: t.Annotated[UploadFile, params.File()],
) -> t.Annotated[JsonResponse, ResponseSpec(model=Resp)]:
    return JsonResponse(Resp(message="hello"))


async def endpoint4(
    request: HttpRequest,
    jsn2: t.Annotated[Jsn2, params.Json()],
) -> t.Annotated[JsonResponse, ResponseSpec(model=Resp2)]:
    return JsonResponse(Resp2(resp=Resp(message="hello"), code=200))


def test_openapi_create() -> None:
    route = Route(
        "/endpoint1",
        endpoint=endpoint1,
        tags=["tag1"],
        methods=["GET"],
        summary="endpoint1 summary",
        description="endpoint1 description",
        externalDocs={"url": "http://example.com", "description": "example"},
        operation_id="endpoint1_operation",
    )
    route2 = Route(
        "/endpoint2", endpoint=endpoint2, tags=["tag1", "tag2"], methods=["POST"]
    )

    route3 = Route(
        "/endpoint3",
        endpoint=endpoint3,
        tags=["tag1"],
        methods=["POST"],
        summary="endpoint3 summary",
    )

    route4 = Route(
        "/endpoint4",
        endpoint=endpoint4,
        tags=["tag1"],
        methods=["POST"],
        summary="endpoint4 summary",
    )

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
        [route, route2, route3, route4],
        openapi_setting=openapi_setting,
    )

    # version
    assert ret.openapi == "3.1.1"

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
    assert len(ret.paths) == 4

    # endpoint1
    assert "/endpoint1" in ret.paths
    pathitem: s.PathItem = ret.paths["/endpoint1"]

    assert pathitem.get is not None
    assert pathitem.post is None
    assert pathitem.get.operationId == "endpoint1_operation"

    # parameters
    parameters: t.List[s.Parameter] = t.cast(
        t.List[s.Parameter], pathitem.get.parameters
    )
    assert parameters is not None

    params = [p.name for p in parameters]
    assert "pth1" in params
    assert "pth2" in params

    # responses
    responses: s.Responses = t.cast(s.Responses, pathitem.get.responses)

    assert responses is not None
    assert "200" in responses

    response: s.Response = t.cast(s.Response, responses["200"])

    content: t.Dict[str, s.MediaType] = t.cast(
        t.Dict[str, s.MediaType], response.content
    )
    assert "application/json" in content

    media: s.MediaType = t.cast(s.MediaType, content["application/json"])  # type: ignore

    assert media.media_type_schema is not None
    assert isinstance(media.media_type_schema, s.Reference)
    assert media.media_type_schema.ref is not None

    # endpoint2
    assert "/endpoint2" in ret.paths
    pathitem: s.PathItem = ret.paths["/endpoint2"]

    assert pathitem.post is not None
    assert pathitem.get is None

    # parameters
    parameters: t.List[s.Parameter] = t.cast(
        t.List[s.Parameter], pathitem.post.parameters
    )
    assert parameters is not None

    # check cookie and header
    assert len(parameters) == 5
    params = [p.name for p in parameters]  # type: ignore
    assert "hdr1" in params
    assert "hdr2" in params
    assert "hdr3-alias" in params
    assert "ckie1" in params
    assert "ckie2" in params

    # request body
    request_body: s.RequestBody = t.cast(s.RequestBody, pathitem.post.requestBody)
    assert request_body is not None
    assert "application/json" in request_body.content
    media: s.MediaType = request_body.content["application/json"]
    assert media.media_type_schema is not None

    # endpoint3
    pathitem = ret.paths["/endpoint3"]

    assert pathitem.post is not None
    assert pathitem.get is None

    # parameters
    parameters: t.List[s.Parameter] = t.cast(
        t.List[s.Parameter], pathitem.post.parameters
    )
    assert parameters == []

    # request body
    request_body: s.RequestBody = t.cast(s.RequestBody, pathitem.post.requestBody)
    assert request_body is not None
    assert "multipart/form-data" in request_body.content
    media: s.MediaType = request_body.content["multipart/form-data"]

    assert media.media_type_schema is not None

    # endpoint4
    pathitem4 = ret.paths["/endpoint4"]
    assert pathitem4.post is not None

    # response body

    responses: s.Responses = t.cast(s.Responses, pathitem4.post.responses)
    assert responses is not None
    assert "200" in responses

    response: s.Response = t.cast(s.Response, responses["200"])
    assert response.content is not None
    assert "application/json" in response.content
    media: s.MediaType = response.content["application/json"]
    assert media.media_type_schema is not None

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
