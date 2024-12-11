import orjson as json
from pydantic import BaseModel

from unfazed.http import HttpResponse
from unfazed.utils import generic_response


class ResponseModel(BaseModel):
    message: str


def test_generic_response() -> None:
    resp1 = HttpResponse(content="Hello, World!")

    assert generic_response(resp1) == resp1

    resp2 = {"message": "Hello, World!"}
    assert generic_response(resp2).body == json.dumps(resp2)

    resp3 = ResponseModel(message="Hello, World!")
    assert generic_response(resp3).body == json.dumps(resp3.model_dump())

    resp4 = "Hello, World!"
    assert generic_response(resp4).body == resp4.encode()
