import typing as t

from pydantic import BaseModel, Field

from unfazed.file import UploadFile
from unfazed.http import HttpRequest, JsonResponse
from unfazed.openapi import OpenApi
from unfazed.route import Route, params
from unfazed.route.params import ResponseSpec
from unfazed.schema import OpenAPI


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

    schema = ret.model_dump(by_alias=True, exclude_none=True, mode="json")
    import json

    print(json.dumps(schema, indent=2))

    raise Exception("stop")
