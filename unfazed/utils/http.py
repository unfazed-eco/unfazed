import typing as t

from pydantic import BaseModel

from unfazed.http import HttpResponse, JsonResponse
from unfazed.type import GenericReponse


def generic_response(ret: GenericReponse) -> HttpResponse:
    if isinstance(ret, HttpResponse):
        return ret
    elif isinstance(ret, (t.Dict, BaseModel)):
        return JsonResponse(ret)
    else:
        return HttpResponse(ret)
