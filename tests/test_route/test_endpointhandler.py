import typing as t

import pytest
from pydantic import BaseModel, Field

from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import Route
from unfazed.route import params as p


async def reiceive(*args, **kw):
    # yield body

    yield {
        "type": "http.request",
        "body": b'{"path1": "foo", "path2": 1, "path3": 2, "path4": "foo2", "path5": "foo3", "path6": "foo4"}',
        "more_body": False,
    }

    yield {
        "type": "http.request",
        "body": b"",
    }


async def send(*args, **kw):
    pass


# ====== test path ======
class Pth1(BaseModel):
    path1: str
    path2: int = Field(default=1)


class Pth2(BaseModel):
    path3: int
    path4: str = Field(default="123")


class RespE1(BaseModel):
    path1: str
    path2: int
    path3: int
    path4: str
    path5: str
    path6: str


async def endpoint1(
    request: HttpRequest,
    pth1: t.Annotated[Pth1, p.Path()],
    pth2: t.Annotated[Pth2, p.Path()],
    path5: t.Annotated[str, p.PathField(default="foo")],
    q1: int = 1,
    path6: str = "bar",
) -> t.Annotated[JsonResponse[RespE1], p.ResponseSpec(model=RespE1)]:
    r = RespE1(
        path1=pth1.path1,
        path2=pth1.path2,
        path3=pth2.path3,
        path4=pth2.path4,
        path5=path5,
        path6=path6,
    )
    return JsonResponse(r)


@pytest.mark.asyncio
async def test_path():
    route = Route(
        path="/{path1}/{path2}/{path3}/{path4}/{path5}/{path6}",
        endpoint=endpoint1,
        tags=["tag1"],
    )

    definition = route.endpoint_definition

    assert "pth1" in definition.params
    assert "pth2" in definition.params
    assert "path5" in definition.params
    assert "path6" in definition.params
    assert "pth1" in definition.path_params and definition.path_params["pth1"] == (
        Pth1,
        ...,
    )
    assert "pth2" in definition.path_params and definition.path_params["pth2"] == (
        Pth2,
        ...,
    )
    assert (
        "path5" in definition.path_params
        and definition.path_params["path5"][0] is str
        and definition.path_params["path5"][1].default == "foo"
    )
    assert (
        "path6" in definition.path_params
        and definition.path_params["path6"][0] is str
        and definition.path_params["path6"][1].default == "bar"
    )
    assert "q1" not in definition.path_params

    pathmodel: BaseModel = definition.path_model
    for ele in ["path1", "path2", "path3", "path4", "path5", "path6"]:
        assert ele in pathmodel.model_fields

    scope = {
        "type": "http",
        "method": "GET",
        "scheme": "https",
        "server": ("www.example.org", 80),
        "path": "/foo/1/2/foo2/foo3/foo4",
        "headers": [],
        "query_string": b"",
    }

    # wait endpoint1 to be called and validate
    await route(scope=scope, receive=reiceive, send=send)


# ====== test query ======


class Qry1(BaseModel):
    query1: str
    query2: int = Field(default=1)


class Qry2(BaseModel):
    query3: int
    query4: str = Field(default="123")


class RespE2(BaseModel):
    query1: str
    query2: int
    query3: int
    query4: str
    query5: str
    query6: str


async def endpoint2(
    request: HttpRequest,
    qry1: t.Annotated[Qry1, p.Query()],
    qry2: t.Annotated[Qry2, p.Query()],
    query5: t.Annotated[str, p.QueryField(default="foo")],
    query6: str = "bar",
) -> t.Annotated[JsonResponse[RespE2], p.ResponseSpec(model=RespE2)]:
    r = RespE2(
        query1=qry1.query1,
        query2=qry1.query2,
        query3=qry2.query3,
        query4=qry2.query4,
        query5=query5,
        query6=query6,
    )
    return JsonResponse(r)


@pytest.mark.asyncio
async def test_query():
    route = Route(
        path="/",
        endpoint=endpoint2,
        tags=["tag1"],
    )

    definition = route.endpoint_definition

    assert "qry1" in definition.params
    assert "qry2" in definition.params
    assert "query5" in definition.params
    assert "query6" in definition.params
    assert "qry1" in definition.query_params and definition.query_params["qry1"] == (
        Qry1,
        ...,
    )
    assert "qry2" in definition.query_params and definition.query_params["qry2"] == (
        Qry2,
        ...,
    )
    assert (
        "query5" in definition.query_params
        and definition.query_params["query5"][0] is str
        and definition.query_params["query5"][1].default == "foo"
    )
    assert (
        "query6" in definition.query_params
        and definition.query_params["query6"][0] is str
        and definition.query_params["query6"][1].default == "bar"
    )

    # assert "qry1" in definition.query_model.model_fields
    # assert "qry2" in definition.query_model.model_fields
    # assert "query5" in definition.query_model.model_fields
    # assert "query6" in definition.query_model.model_fields

    querymodel = definition.query_model
    for ele in ["query1", "query2", "query3", "query4", "query5", "query6"]:
        assert ele in querymodel.model_fields

    scope = {
        "type": "http",
        "method": "GET",
        "scheme": "https",
        "server": ("www.example.org", 80),
        "path": "/",
        "headers": [],
        "query_string": b"query1=foo&query2=1&query3=2&query4=foo2&query5=foo3&query6=foo4",
    }

    # wait endpoint2 to be called and validate
    await route(scope=scope, receive=reiceive, send=send)


# ====== test header ======


class Hdr1(BaseModel):
    header1: str
    header2: int = Field(default=1)


class Hdr2(BaseModel):
    header3: int
    header4: str = Field(default="123")


class RespE3(BaseModel):
    header1: str
    header2: int
    header3: int
    header4: str
    header5: str


async def endpoint3(
    request: HttpRequest,
    hdr1: t.Annotated[Hdr1, p.Header()],
    hdr2: t.Annotated[Hdr2, p.Header()],
    header5: t.Annotated[str, p.HeaderField(default="foo")],
) -> t.Annotated[JsonResponse[RespE3], p.ResponseSpec(model=RespE3)]:
    r = RespE3(
        header1=hdr1.header1,
        header2=hdr1.header2,
        header3=hdr2.header3,
        header4=hdr2.header4,
        header5=header5,
    )
    return JsonResponse(r)


@pytest.mark.asyncio
async def test_header():
    route = Route(
        path="/",
        endpoint=endpoint3,
        tags=["tag1"],
    )

    definition = route.endpoint_definition

    assert "hdr1" in definition.params
    assert "hdr2" in definition.params
    assert "header5" in definition.params

    assert "hdr1" in definition.header_params and definition.header_params["hdr1"] == (
        Hdr1,
        ...,
    )

    assert "hdr2" in definition.header_params and definition.header_params["hdr2"] == (
        Hdr2,
        ...,
    )

    assert (
        "header5" in definition.header_params
        and definition.header_params["header5"][0] is str
        and definition.header_params["header5"][1].default == "foo"
    )

    for ele in ["header1", "header2", "header3", "header4", "header5"]:
        assert ele in definition.header_model.model_fields

    scope = {
        "type": "http",
        "method": "GET",
        "scheme": "https",
        "server": ("www.example.org", 80),
        "path": "/",
        "headers": [
            (b"header1", b"foo"),
            (b"header2", b"1"),
            (b"header3", b"2"),
            (b"header4", b"foo2"),
            (b"header5", b"foo3"),
        ],
        "query_string": b"",
    }

    # wait endpoint3 to be called and validate
    await route(scope=scope, receive=reiceive, send=send)


# ====== test cookie ======


class Ckie1(BaseModel):
    cookie1: str
    cookie2: int = Field(default=1)


class Ckie2(BaseModel):
    cookie3: int
    cookie4: str = Field(default="123")


class RespE4(BaseModel):
    cookie1: str
    cookie2: int
    cookie3: int
    cookie4: str
    cookie5: str


async def endpoint4(
    request: HttpRequest,
    ck1: t.Annotated[Ckie1, p.Cookie()],
    ck2: t.Annotated[Ckie2, p.Cookie()],
    cookie5: t.Annotated[str, p.CookieField(default="foo")],
) -> t.Annotated[JsonResponse[RespE4], p.ResponseSpec(model=RespE4)]:
    r = RespE4(
        cookie1=ck1.cookie1,
        cookie2=ck1.cookie2,
        cookie3=ck2.cookie3,
        cookie4=ck2.cookie4,
        cookie5=cookie5,
    )
    return JsonResponse(r)


@pytest.mark.asyncio
async def test_cookie():
    route = Route(
        path="/",
        endpoint=endpoint4,
        tags=["tag1"],
    )

    definition = route.endpoint_definition

    assert "ck1" in definition.params
    assert "ck2" in definition.params
    assert "cookie5" in definition.params

    assert "ck1" in definition.cookie_params and definition.cookie_params["ck1"] == (
        Ckie1,
        ...,
    )

    assert "ck2" in definition.cookie_params and definition.cookie_params["ck2"] == (
        Ckie2,
        ...,
    )

    assert (
        "cookie5" in definition.cookie_params
        and definition.cookie_params["cookie5"][0] is str
        and definition.cookie_params["cookie5"][1].default == "foo"
    )

    for ele in ["cookie1", "cookie2", "cookie3", "cookie4", "cookie5"]:
        assert ele in definition.cookie_model.model_fields

    scope = {
        "type": "http",
        "method": "GET",
        "scheme": "https",
        "server": ("www.example.org", 80),
        "path": "/",
        "headers": [
            (
                b"cookie",
                b"cookie1=foo; cookie2=1; cookie3=2; cookie4=foo2; cookie5=foo3",
            ),
        ],
        "query_string": b"",
    }

    # wait endpoint4 to be called and validate
    await route(scope=scope, receive=reiceive, send=send)


# ====== test body ======


class Body1(BaseModel):
    body1: str
    body2: int = Field(default=1)


class Body2(BaseModel):
    body3: int
    body4: str = Field(default="123")


class Body3(BaseModel):
    body5: str


class RespE5(BaseModel):
    body1: str
    body2: int
    body3: int
    body4: str
    body5: str


async def endpoint5(
    request: HttpRequest,
    bd1: t.Annotated[Body1, p.Body()],
    bd2: t.Annotated[Body2, p.Body()],
    bd3: Body3,
    body6: t.Annotated[str, p.BodyField(default="foo")],
) -> t.Annotated[JsonResponse[RespE5], p.ResponseSpec(model=RespE5)]:
    r = RespE5(
        body1=bd1.body1,
        body2=bd1.body2,
        body3=bd2.body3,
        body4=bd2.body4,
        body5=bd3.body5,
        body6=body6,
    )
    return JsonResponse(r)


@pytest.mark.asyncio
async def test_body():
    route = Route(
        path="/",
        endpoint=endpoint5,
        tags=["tag1"],
    )

    definition = route.endpoint_definition

    assert "bd1" in definition.params
    assert "bd2" in definition.params
    assert "bd3" in definition.params
    assert "body6" in definition.params

    assert "bd1" in definition.body_params and definition.body_params["bd1"] == (
        Body1,
        ...,
    )

    assert "bd2" in definition.body_params and definition.body_params["bd2"] == (
        Body2,
        ...,
    )

    assert "bd3" in definition.body_params and definition.body_params["bd3"] == (
        Body3,
        ...,
    )

    assert (
        "body6" in definition.body_params
        and definition.body_params["body6"][0] is str
        and definition.body_params["body6"][1].default == "foo"
    )

    for ele in ["body1", "body2", "body3", "body4", "body5", "body6"]:
        assert ele in definition.body_model.model_fields

    scope = {
        "type": "http",
        "method": "POST",
        "scheme": "https",
        "server": ("www.example.org", 80),
        "path": "/",
        "headers": [],
        "query_string": b"",
        "body": b'{"body1": "foo", "body2": 1, "body3": 2, "body4": "foo2", "body5": "foo3"}',
    }

    # wait endpoint5 to be called and validate
    await route(scope=scope, receive=reiceive, send=send)
