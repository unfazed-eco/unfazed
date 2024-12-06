import typing as t

from pydantic import BaseModel

from unfazed.http import HttpResponse, JsonResponse
from unfazed.type import GenericReponse


def generic_response(ret: GenericReponse) -> HttpResponse:
    """
    Generic response for unfazed.

    Example:
        ```python

        from unfazed.http import HttpResponse
        from unfazed.utils import generic_response

        resp1 = generic_response(HttpResponse(content="Hello, World!"))
        resp2 = generic_response({"message": "Hello, World!"})
        resp3 = generic_response(ResponseModel(message="Hello, World!"))
        resp4 = generic_response("Hello, World!")

        ```
    """
    if isinstance(ret, HttpResponse):
        return ret
    elif isinstance(ret, (t.Dict, BaseModel, t.List)):
        return JsonResponse(ret)
    else:
        return HttpResponse(ret)
