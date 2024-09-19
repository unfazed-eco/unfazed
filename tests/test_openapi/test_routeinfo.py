from pydantic import BaseModel

from unfazed.http import HttpRequest, HttpResponse
from unfazed.openapi import RouteInfo
from unfazed.openapi import params as p
from unfazed.openapi.spec import Tag
from unfazed.route import Route


# test request
async def view1(request: HttpRequest) -> HttpResponse:
    pass


async def view2(
    request: HttpRequest,
    path1: str = p.Path(),
    path2: int = p.Path(),
) -> HttpResponse:
    pass


async def view3(
    request: HttpRequest,
    query1: str = p.Query(),
    query2: str = p.Query(),
) -> HttpResponse:
    pass


class Ctx(BaseModel):
    name: str
    age: int


async def view4(
    request: HttpRequest,
    ctx: Ctx,
) -> HttpResponse:
    pass


async def view5(request: HttpRequest, ctx: Ctx = p.Body()) -> HttpResponse:
    pass


async def view6(request: HttpRequest, token: str = p.Header()) -> HttpResponse:
    pass


async def view7(request: HttpRequest, token: str = p.Cookie()) -> HttpResponse:
    pass


# test response
def test_request():
    r1 = Route(path="/", endpoint=view1, tags=["tag1"])

    ri1 = RouteInfo(
        endpoint=r1.endpoint,
        methods=r1.methods,
        tags=[Tag(name=tag) for tag in r1.tags],
        path_parm_names=r1.param_convertors.keys(),
    )

    assert ri1.methods == ["GET"]

    r2 = Route(
        path="/{path1}/{path2}",
        endpoint=view2,
        methods=["POST"],
        tags=["tag2"],
    )

    ri2 = RouteInfo(
        endpoint=r2.endpoint,
        methods=r2.methods,
        tags=[Tag(name=tag) for tag in r2.tags],
        path_parm_names=r2.param_convertors.keys(),
    )

    assert ri2.methods == ["POST"]
    assert ri2.path_parm_names == ["path1", "path2"]

    r3 = Route(
        path="/",
        endpoint=view3,
        tags=["tag3"],
    )

    ri3 = RouteInfo(
        endpoint=r3.endpoint,
        methods=r3.methods,
        tags=[Tag(name=tag) for tag in r3.tags],
        path_parm_names=r3.param_convertors.keys(),
    )

    print(ri3)
