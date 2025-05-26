import os
import typing as t

import pytest
from pydantic import BaseModel, Field
from starlette.routing import Match

from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed
from unfazed.exception import TypeHintRequired
from unfazed.file import UploadFile
from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import Route
from unfazed.route import params as p
from unfazed.route.endpoint import EndPointDefinition
from unfazed.test import Requestfactory
from unfazed.type import Receive


async def _reiceive() -> t.AsyncGenerator[t.MutableMapping[str, t.Any], None]:
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


# cope with mypy checking
reiceive = t.cast(Receive, _reiceive)


async def send(*args: t.Any, **kw: t.Any) -> None:
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
    path5: t.Annotated[str, p.Path(default="foo")],
    path6: str,
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=RespE1)]:
    r = RespE1(
        path1=pth1.path1,
        path2=pth1.path2,
        path3=pth2.path3,
        path4=pth2.path4,
        path5=path5,
        path6=path6,
    )
    return JsonResponse(r)


async def test_path() -> None:
    route = Route(
        path="/{path1}/{path2}/{path3}/{path4}/{path5}/{path6}",
        endpoint=endpoint1,
        tags=["tag1"],
    )

    definition = route.endpoint_definition

    assert definition.params is not None
    assert "pth1" in definition.params
    assert "pth2" in definition.params
    assert "path5" in definition.params
    assert "path6" in definition.params

    assert definition.path_params is not None
    assert (
        "pth1" in definition.path_params
        and definition.path_params["pth1"][0] == Pth1
        and isinstance(definition.path_params["pth1"][1], p.Path)
    )
    assert (
        "pth2" in definition.path_params
        and definition.path_params["pth2"][0] == Pth2
        and isinstance(definition.path_params["pth1"][1], p.Path)
    )
    assert (
        "path5" in definition.path_params
        and definition.path_params["path5"][0] is str
        and definition.path_params["path5"][1].default == "foo"
    )
    assert (
        "path6" in definition.path_params and definition.path_params["path6"][0] is str
    )

    pathmodel = definition.path_model
    assert pathmodel is not None
    for ele in ["path1", "path2", "path3", "path4", "path5", "path6"]:
        assert ele in pathmodel.model_fields

    # params_model
    assert len([i for i in definition.param_models if i]) == 1

    scope = {
        "type": "http",
        "method": "GET",
        "scheme": "https",
        "server": ("www.unfazed.org", 80),
        "path": "/foo/1/2/foo2/foo3/foo4",
        "headers": [],
        "query_string": b"",
    }
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
    query5: t.Annotated[str, p.Query(default="foo")],
    query6: str,
    query7: t.Annotated[str, p.Query(default="")],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=RespE2)]:
    r = RespE2(
        query1=qry1.query1,
        query2=qry1.query2,
        query3=qry2.query3,
        query4=qry2.query4,
        query5=query5,
        query6=query6,
    )
    return JsonResponse(r)


def syncendpoint2(
    request: HttpRequest,
    qry1: t.Annotated[Qry1, p.Query()],
    qry2: t.Annotated[Qry2, p.Query()],
    query5: t.Annotated[str, p.Query(default="foo")],
    query6: str,
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=RespE2)]:
    r = RespE2(
        query1=qry1.query1,
        query2=qry1.query2,
        query3=qry2.query3,
        query4=qry2.query4,
        query5=query5,
        query6=query6,
    )
    return JsonResponse(r)


async def test_query() -> None:
    route = Route(
        path="/",
        endpoint=endpoint2,
        methods=["GET"],
        app_label="test.query",
    )

    definition = route.endpoint_definition

    assert definition.params is not None
    assert "qry1" in definition.params
    assert "qry2" in definition.params
    assert "query5" in definition.params
    assert "query6" in definition.params

    assert definition.query_params is not None
    assert (
        "qry1" in definition.query_params
        and definition.query_params["qry1"][0] == Qry1
        and isinstance(definition.query_params["qry1"][1], p.Query)
    )
    assert (
        "qry2" in definition.query_params
        and definition.query_params["qry2"][0] == Qry2
        and isinstance(definition.query_params["qry2"][1], p.Query)
    )
    assert (
        "query5" in definition.query_params
        and definition.query_params["query5"][0] is str
        and definition.query_params["query5"][1].default == "foo"
    )
    assert (
        "query6" in definition.query_params
        and definition.query_params["query6"][0] is str
    )

    querymodel = definition.query_model
    assert querymodel is not None
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


async def test_query_sync() -> None:
    route = Route(
        path="/",
        endpoint=syncendpoint2,
        tags=["tag1"],
    )

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


async def test_query_failed_slove() -> None:
    route = Route(
        path="/",
        endpoint=endpoint2,
        tags=["tag1"],
    )

    with pytest.raises(ExceptionGroup):
        scope = {
            "type": "http",
            "method": "GET",
            "scheme": "https",
            "server": ("www.example.org", 80),
            "path": "/",
            "headers": [],
            "query_string": b"query1=foo&query2=1&query3=errortype&query4=foo2&query5=foo3",
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
    header5: t.Annotated[str, p.Header(default="foo")],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=RespE3)]:
    r = RespE3(
        header1=hdr1.header1,
        header2=hdr1.header2,
        header3=hdr2.header3,
        header4=hdr2.header4,
        header5=header5,
    )
    return JsonResponse(r)


async def test_header() -> None:
    route = Route(
        path="/",
        endpoint=endpoint3,
        tags=["tag1"],
    )

    definition = route.endpoint_definition

    assert definition.params is not None
    assert "hdr1" in definition.params
    assert "hdr2" in definition.params
    assert "header5" in definition.params

    assert definition.header_params is not None
    assert (
        "hdr1" in definition.header_params
        and definition.header_params["hdr1"][0] == Hdr1
        and isinstance(definition.header_params["hdr1"][1], p.Header)
    )

    assert (
        "hdr2" in definition.header_params
        and definition.header_params["hdr2"][0] == Hdr2
        and isinstance(definition.header_params["hdr2"][1], p.Header)
    )

    assert (
        "header5" in definition.header_params
        and definition.header_params["header5"][0] is str
        and definition.header_params["header5"][1].default == "foo"
    )

    assert definition.header_model is not None
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
    cookie5: t.Annotated[str, p.Cookie(default="foo")],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=RespE4)]:
    r = RespE4(
        cookie1=ck1.cookie1,
        cookie2=ck1.cookie2,
        cookie3=ck2.cookie3,
        cookie4=ck2.cookie4,
        cookie5=cookie5,
    )
    return JsonResponse(r)


async def test_cookie() -> None:
    route = Route(
        path="/",
        endpoint=endpoint4,
        tags=["tag1"],
    )

    definition = route.endpoint_definition

    assert definition.params is not None
    assert "ck1" in definition.params
    assert "ck2" in definition.params
    assert "cookie5" in definition.params

    assert definition.cookie_params is not None
    assert (
        "ck1" in definition.cookie_params
        and definition.cookie_params["ck1"][0] == Ckie1
        and isinstance(definition.cookie_params["ck1"][1], p.Cookie)
    )

    assert (
        "ck2" in definition.cookie_params
        and definition.cookie_params["ck2"][0] == Ckie2
        and isinstance(definition.cookie_params["ck2"][1], p.Cookie)
    )

    assert (
        "cookie5" in definition.cookie_params
        and definition.cookie_params["cookie5"][0] is str
        and definition.cookie_params["cookie5"][1].default == "foo"
    )

    assert definition.cookie_model is not None
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

    model_config = {
        "json_schema_extra": {"foo": "bar"},
    }


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
    bd1: t.Annotated[Body1, p.Json()],
    bd2: t.Annotated[Body2, p.Json()],
    bd3: Body3,
    body6: t.Annotated[str, p.Json(default="foo")],
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=RespE5)]:
    r = RespE5(
        body1=bd1.body1,
        body2=bd1.body2,
        body3=bd2.body3,
        body4=bd2.body4,
        body5=bd3.body5,
    )
    return JsonResponse(r)


async def body_receive(*args: t.Any, **kw: t.Any) -> t.Dict:
    return {
        "type": "http.request",
        "body": b'{"body1": "foo", "body2": 1, "body3": 2, "body4": "foo2", "body5": "foo3"}',
        "more_body": False,
    }


async def test_body() -> None:
    route = Route(path="/", endpoint=endpoint5, tags=["tag1"], methods=["POST"])

    definition = route.endpoint_definition

    assert definition.params is not None
    assert "bd1" in definition.params
    assert "bd2" in definition.params
    assert "bd3" in definition.params
    assert "body6" in definition.params

    assert definition.body_params is not None
    assert (
        "bd1" in definition.body_params
        and definition.body_params["bd1"][0] == Body1
        and isinstance(definition.body_params["bd1"][1], p.Json)
    )

    assert (
        "bd2" in definition.body_params
        and definition.body_params["bd2"][0] == Body2
        and isinstance(definition.body_params["bd2"][1], p.Json)
    )
    assert "bd3" in definition.body_params and definition.body_params["bd3"][0] == Body3

    assert (
        "body6" in definition.body_params
        and definition.body_params["body6"][0] is str
        and definition.body_params["body6"][1].default == "foo"
    )

    assert definition.body_model is not None
    for ele in ["body1", "body2", "body3", "body4", "body5", "body6"]:
        assert ele in definition.body_model.model_fields

    fieldinfo6 = definition.body_model.model_fields["body6"]
    assert fieldinfo6.default == "foo"

    ret = definition.body_model.model_config["json_schema_extra"]
    assert "foo" in t.cast(t.Dict, ret)

    scope = {
        "type": "http",
        "method": "POST",
        "scheme": "https",
        "server": ("www.example.org", 80),
        "path": "/",
        "headers": [],
        "query_string": b"",
    }

    assert route.matches(scope)[0] == Match.FULL

    # wit endpoaint5 to be called and validate
    await route(scope=scope, receive=body_receive, send=send)


# === test form =====


class Form1(BaseModel):
    form1: str
    form2: int = Field(default=1)


class Form2(BaseModel):
    form3: int
    form4: str = Field(default="123")


class RespE6(BaseModel):
    form1: str
    form2: int
    form3: int
    form4: str
    form5: str


async def endpoint6(
    request: HttpRequest,
    form1: t.Annotated[Form1, p.Form()],
    form2: t.Annotated[Form2, p.Form()],
    form5: t.Annotated[str, p.Form(default="foo")],
    *args: t.Any,
    **kw: t.Any,
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=RespE6)]:
    r = RespE6(
        form1=form1.form1,
        form2=form1.form2,
        form3=form2.form3,
        form4=form2.form4,
        form5=form5,
    )
    return JsonResponse(r)


async def form_receive(*args: t.Any, **kw: t.Any) -> t.Dict:
    return {
        "type": "http.request",
        "body": b"form1=foo&form2=1&form3=2&form4=foo2&form5=foo3",
        "more_body": False,
    }


async def test_form() -> None:
    route = Route(path="/", endpoint=endpoint6, tags=["tag1"], methods=["POST"])

    definition = route.endpoint_definition

    assert definition.body_type == "form"

    assert definition.params is not None
    assert "form1" in definition.params
    assert "form2" in definition.params
    assert "form5" in definition.params

    assert definition.body_params is not None
    assert (
        "form1" in definition.body_params
        and definition.body_params["form1"][0] == Form1
        and isinstance(definition.body_params["form1"][1], p.Form)
    )

    assert (
        "form2" in definition.body_params
        and definition.body_params["form2"][0] == Form2
        and isinstance(definition.body_params["form2"][1], p.Form)
    )

    assert (
        "form5" in definition.body_params
        and definition.body_params["form5"][0] is str
        and definition.body_params["form5"][1].default == "foo"
    )

    assert definition.body_model is not None
    for ele in ["form1", "form2", "form3", "form4", "form5"]:
        assert ele in definition.body_model.model_fields

    scope = {
        "type": "http",
        "method": "POST",
        "scheme": "https",
        "server": ("www.example.org", 80),
        "path": "/",
        "headers": [
            (b"content-type", b"application/x-www-form-urlencoded"),
        ],
        "query_string": b"",
    }

    assert route.matches(scope)[0] == Match.FULL
    await route(scope=scope, receive=form_receive, send=send)


# === test failed slove =====


async def body_receive2(*args: t.Any, **kw: t.Any) -> t.Dict:
    return {
        "type": "http.request",
        "body": b'{"bd1": "error_body"}',
        "more_body": False,
    }


async def form_receive2(*args: t.Any, **kw: t.Any) -> t.Dict:
    return {
        "type": "http.request",
        "body": b'{"form1": "error_form"}',
        "more_body": False,
    }


async def endpoint7(
    request: HttpRequest,
    pth1: t.Annotated[int, p.Path()],
    bd1: t.Annotated[int, p.Json()],
    cookie1: t.Annotated[int, p.Cookie()],
    hdr1: t.Annotated[int, p.Header()],
) -> JsonResponse:
    return JsonResponse({"pth": pth1})


async def endpoint8(
    request: HttpRequest, form1: t.Annotated[int, p.Form()]
) -> JsonResponse:
    return JsonResponse({"form": form1})


async def test_failed_slove() -> None:
    route = Route(
        path="/{pth1}",
        endpoint=endpoint7,
        tags=["tag1"],
        methods=["POST"],
    )

    scope = {
        "type": "http",
        "method": "POST",
        "scheme": "https",
        "server": ("www.example.org", 80),
        "path": "/error_path",
        "headers": [(b"hdr1", b"error_header"), (b"cookie", b"cookie1=error_cookie")],
        "query_string": b"",
    }

    assert route.matches(scope)[0] == Match.FULL

    with pytest.raises(ExceptionGroup):
        await route(scope=scope, receive=body_receive2, send=send)

    route = Route(
        path="/{pth1}",
        endpoint=endpoint8,
        tags=["tag1"],
        methods=["POST"],
    )

    scope = {
        "type": "http",
        "method": "POST",
        "scheme": "https",
        "server": ("www.example.org", 80),
        "path": "/error_path",
        "headers": [
            (b"content-type", b"application/x-www-form-urlencoded"),
        ],
    }

    with pytest.raises(ExceptionGroup):
        await route(scope=scope, receive=form_receive2, send=send)


# ====== test definition ======


class EndpointView:
    def get(
        self, request: HttpRequest, qry1: t.Annotated[str, p.Query()]
    ) -> JsonResponse:
        return JsonResponse({"method": "GET"})


async def endpoint9(
    request: HttpRequest, qry1: t.Annotated[str, p.Query()] = "foo"
) -> JsonResponse:
    return JsonResponse({"method": "GET"})


async def endpoint10(
    request: HttpRequest, qry1: t.Annotated[bytes, p.Query(default="foo")]
) -> JsonResponse:
    return JsonResponse({"method": "GET"})


async def endpoint11(request: HttpRequest):  # type: ignore
    return JsonResponse({"method": "GET"})


class RespE121(BaseModel):
    age: int


class RespE122(BaseModel):
    method: str


async def endpoint12(
    request: HttpRequest,
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=RespE121)]:
    return JsonResponse({"method": "GET"})


class Body13(BaseModel):
    name: str


async def endpoint13(
    request: HttpRequest, form1: t.Annotated[str, p.Form()], bd1: Body13
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=RespE122)]:
    return JsonResponse({"method": "GET"})


async def endpoint14(
    request: HttpRequest, form1: t.Annotated[str, "wrong meta"]
) -> JsonResponse:
    return JsonResponse({"method": "GET"})


async def endpoint15(
    request: HttpRequest,
    form1: t.Annotated[str, p.Form(default="foo")],
    body1: t.Annotated[str, p.Json(default="foo")],
) -> JsonResponse:
    return JsonResponse({"method": "GET"})


async def endpoint16(
    request: HttpRequest,
    body1: t.Annotated[str, p.Json(default="foo")],
    form1: t.Annotated[str, p.Form(default="foo")],
) -> JsonResponse:
    return JsonResponse({"method": "GET"})


class Body171(BaseModel):
    name: str


class Body172(BaseModel):
    name: str


async def endpoint17(
    request: HttpRequest,
    bd1: Body171,
    bd2: Body172,
) -> JsonResponse:
    return JsonResponse({"method": "POST"})


async def endpoint18(
    request: HttpRequest,
    bd1: Body171,
    name: t.Annotated[str, p.Json()],
) -> JsonResponse:
    return JsonResponse({"method": "POST"})


async def endpoint20(  # type: ignore
    request: HttpRequest,
    bd1,
) -> JsonResponse:
    return JsonResponse({"method": "POST"})


async def test_definition() -> None:
    # support class view
    # but not recommended
    endpointview = EndpointView()
    ed = EndPointDefinition(
        endpoint=endpointview.get,
        methods=["GET"],
        tags=["tag1"],
        path_parm_names=[],
        debug=True,
    )

    assert ed.params is not None
    assert "self" not in ed.params
    assert "qry1" in ed.params

    # dont support default value
    with pytest.raises(ValueError):
        EndPointDefinition(
            endpoint=endpoint9,
            methods=["GET"],
            tags=["tag1"],
            path_parm_names=[],
        )

    # only str/int/float/dict/basemodel are supported

    with pytest.raises(ValueError):
        EndPointDefinition(
            endpoint=endpoint10,
            methods=["GET"],
            tags=["tag1"],
            path_parm_names=[],
        )

    # must have return type
    with pytest.raises(TypeHintRequired):
        EndPointDefinition(
            endpoint=endpoint11,
            methods=["GET"],
            tags=["tag1"],
            path_parm_names=[],
        )

    # support response models
    ed = EndPointDefinition(
        endpoint=endpoint12,
        methods=["GET"],
        tags=["tag1"],
        path_parm_names=[],
        response_models=[p.ResponseSpec(model=RespE122)],
    )

    assert ed.response_models is not None
    assert ed.response_models[0].model == RespE122

    # body / form conflict
    with pytest.raises(ValueError):
        EndPointDefinition(
            endpoint=endpoint13,
            methods=["GET"],
            tags=["tag1"],
            path_parm_names=[],
        )

    with pytest.raises(ValueError):
        EndPointDefinition(
            endpoint=endpoint15,
            methods=["GET"],
            tags=["tag1"],
            path_parm_names=[],
        )

    with pytest.raises(ValueError):
        EndPointDefinition(
            endpoint=endpoint16,
            methods=["GET"],
            tags=["tag1"],
            path_parm_names=[],
        )

    # wrong meta
    with pytest.raises(ValueError):
        EndPointDefinition(
            endpoint=endpoint14,
            methods=["GET"],
            tags=["tag1"],
            path_parm_names=[],
        )

    # field conflict
    with pytest.raises(ValueError):
        EndPointDefinition(
            endpoint=endpoint17,
            methods=["POST"],
            tags=["tag1"],
            path_parm_names=[],
        )

    with pytest.raises(ValueError):
        EndPointDefinition(
            endpoint=endpoint18,
            methods=["POST"],
            tags=["tag1"],
            path_parm_names=[],
        )

    # missing type hint
    with pytest.raises(TypeHintRequired):
        EndPointDefinition(
            endpoint=endpoint20,
            methods=["POST"],
            tags=["tag1"],
            path_parm_names=[],
        )


# ====== test file ======


class CtxFile(BaseModel):
    name: str
    age: int


class RespFile(BaseModel):
    name: str
    age: int
    file_name: str | None
    content: str | None


async def endpoint19(
    request: HttpRequest,
    file1: t.Annotated[UploadFile, p.File()],
    ctx: t.Annotated[CtxFile, p.Form()],
) -> JsonResponse:
    content_bytes = await file1.read()
    content = content_bytes.decode("utf-8")
    return JsonResponse(
        RespFile(
            name=ctx.name,
            age=ctx.age,
            file_name=file1.filename,
            content=content,
        )
    )


async def test_file() -> None:
    route = Route(
        path="/with-file",
        endpoint=endpoint19,
        tags=["tag1"],
        methods=["POST"],
    )

    definition = route.endpoint_definition

    assert definition.params is not None
    assert "file1" in definition.params
    assert "file1" in definition.body_params
    assert definition.body_model is not None
    assert "file1" in definition.body_model.model_fields

    unfazed = Unfazed(
        settings=UnfazedSettings(PROJECT_NAME="test_file"), routes=[route]
    )

    await unfazed.setup()

    request = Requestfactory(unfazed)

    zenofpython = os.path.join(os.path.dirname(__file__), "zenofpython.txt")

    resp = await request.post(
        "/with-file",
        files={"file1": open(zenofpython, "rb")},
        data={"name": "unfazed", "age": 1},
    )

    assert resp.status_code == 200
    assert "content" in resp.json()
