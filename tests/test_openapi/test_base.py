import typing as t

from pydantic import BaseModel
from pytest_mock import MockerFixture

from unfazed.http import HttpRequest, JsonResponse
from unfazed.openapi import OpenApi
from unfazed.route import Route
from unfazed.route.params import ResponseSpec
from unfazed.schema import OpenAPI


class Ctx(BaseModel):
    page: int
    size: int
    search: str


class Resp(BaseModel):
    message: str


async def endpoint1(
    request: HttpRequest, ctx: Ctx
) -> t.Annotated[JsonResponse[Resp], ResponseSpec(model=Resp)]:
    data = Resp(message="Hello, World!")
    return JsonResponse(data)


def test_openapi_create(mocker: MockerFixture):
    route = Route("/endpoint1", endpoint=endpoint1)

    ret = OpenApi.create_openapi_model(
        [route],
        project_name="myproject",
        version="1.0.0",
        openapi_setting=OpenAPI(servers=["http://localhost:8000"]),
    )

    # print(ret.model_json_schema())

    import json

    print(json.dumps(ret.model_json_schema()))

    raise NotImplementedError
