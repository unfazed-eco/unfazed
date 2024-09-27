import typing as t

from pydantic import BaseModel

from unfazed.http import HttpRequest, HttpResponse
from unfazed.openapi import RouteInfo
from unfazed.route import params as p
from unfazed.openapi import spec as s
from unfazed.route import Route


class PathModel(BaseModel):
    path3: str
    path4: int


class QueryModel(BaseModel):
    query3: str
    query4: int


class BodyModel(BaseModel):
    body4: int
    body5: str


class HeaderModel(BaseModel):
    header2: str
    header3: int


class CookieModel(BaseModel):
    cookie2: str
    cookie3: int


async def endpoint(
    request: HttpRequest,
    path1: str,
    path2: t.Annotated[int, p.PathField()],
    pathmodel: t.Annotated[PathModel, p.Path()],
) -> HttpResponse:
    pass


async def endpoint2(
    request: HttpRequest,
    query1: str,
    query2: t.Annotated[int, p.QueryField()],
    querymodel: t.Annotated[QueryModel, p.Query()],
) -> HttpResponse:
    pass


async def endpoint3(
    body1: BodyModel,
    body2: t.Annotated[BodyModel, p.Body()],
    body3: t.Annotated[str, p.BodyField()],
    header1: t.Annotated[str, p.HeaderField()],
    headermodel: t.Annotated[HeaderModel, p.Header()],
    cookie1: t.Annotated[str, p.CookieField()],
    cookiemodel: t.Annotated[CookieModel, p.Cookie()],
) -> HttpResponse:
    pass


def test_request_params():
    r1 = Route(
        path="/{path1}/{path2}/{path3}/{path4}",
        endpoint=endpoint,
        tags=["tag1"],
    )

    ri1 = RouteInfo(
        endpoint=r1.endpoint,
        methods=r1.methods,
        tags=[s.Tag(name=t) for t in r1.tags],
        path_parm_names=r1.param_convertors.keys(),
    )

    assert "path1" in ri1.params
    assert "path2" in ri1.params
    assert "pathmodel" in ri1.params

    assert len(ri1.path_params) == 3

    r2 = Route(
        path="/",
        endpoint=endpoint2,
        tags=["tag2"],
    )

    ri2 = RouteInfo(
        endpoint=r2.endpoint,
        methods=r2.methods,
        tags=[s.Tag(name=t) for t in r2.tags],
        path_parm_names=r2.param_convertors.keys(),
    )

    assert "query1" in ri2.params
    assert "query2" in ri2.params
    assert "querymodel" in ri2.params

    assert len(ri2.query_params) == 3

    r3 = Route(
        path="/",
        endpoint=endpoint3,
        tags=["tag3"],
    )
    ri3 = RouteInfo(
        endpoint=r3.endpoint,
        methods=r3.methods,
        tags=[s.Tag(name=t) for t in r3.tags],
        path_parm_names=r3.param_convertors.keys(),
    )

    assert "body1" in ri3.params
    assert "body2" in ri3.params
    assert "body3" in ri3.params

    assert len(ri3.body_params) == 3

    assert "header1" in ri3.params
    assert "headermodel" in ri3.params

    assert len(ri3.header_params) == 2
    assert "cookie1" in ri3.params
    assert "cookiemodel" in ri3.params

    assert len(ri3.cookie_params) == 2


async def endpoint4(request: HttpRequest) -> HttpResponse:
    pass


async def endpoint5(
    request: HttpRequest,
) -> t.Annotated[HttpResponse, s.Response(description="response for endpoint5")]:
    pass


def test_resp_params():
    r1 = Route(
        path="/",
        endpoint=endpoint4,
        tags=["tag1"],
    )

    ri1 = RouteInfo(
        endpoint=r1.endpoint,
        methods=r1.methods,
        tags=[s.Tag(name=t) for t in r1.tags],
        path_parm_names=r1.param_convertors.keys(),
    )

    assert ri1.response_models is None

    r2 = Route(
        path="/",
        endpoint=endpoint5,
        tags=["tag2"],
    )

    ri2 = RouteInfo(
        endpoint=r2.endpoint,
        methods=r2.methods,
        tags=[s.Tag(name=t) for t in r2.tags],
        path_parm_names=r2.param_convertors.keys(),
    )

    assert len(ri2.response_models) == 1
    assert ri2.response_models[0].description == "response for endpoint5"

    r3 = Route(
        path="/",
        endpoint=endpoint5,
        tags=["tag2"],
        responses=[s.Response(description="response in route")],
    )
    ri3 = RouteInfo(
        endpoint=r3.endpoint,
        methods=r3.methods,
        tags=[s.Tag(name=t) for t in r3.tags],
        path_parm_names=r3.param_convertors.keys(),
        response_models=r3.responses,
    )

    assert len(ri3.response_models) == 1
    assert ri3.response_models[0].description == "response in route"
