import orjson as json
from pydantic import BaseModel

from unfazed.contrib.common.utils import response_error, response_success


class Body3(BaseModel):
    foo: str
    bar: int


def test_response_success() -> None:
    response1 = response_success(data={"foo": "bar"})

    body1 = json.loads(response1.body)

    assert body1 == {
        "code": 0,
        "message": "success",
        "data": {"foo": "bar"},
    }

    response2 = response_success(data=[1, 2, 3])
    body2 = json.loads(response2.body)

    assert body2 == {
        "code": 0,
        "message": "success",
        "data": [1, 2, 3],
    }

    response3 = response_success(data=Body3(foo="bar", bar=1))

    body3 = json.loads(response3.body)

    assert body3 == {
        "code": 0,
        "message": "success",
        "data": {"foo": "bar", "bar": 1},
    }

    response4 = response_success()
    body4 = json.loads(response4.body)

    assert body4 == {
        "code": 0,
        "message": "success",
        "data": {},
    }


def test_response_error() -> None:
    resp1 = response_error(code=404, message="not found")

    body1 = json.loads(resp1.body)

    assert body1 == {
        "code": 404,
        "message": "not found",
        "data": {},
    }

    resp2 = response_error(
        code=500, message="server error", data=Body3(foo="bar", bar=1)
    )

    body2 = json.loads(resp2.body)

    assert body2 == {
        "code": 500,
        "message": "server error",
        "data": {"foo": "bar", "bar": 1},
    }
