import typing as t

from pydantic import BaseModel

from unfazed.http import JsonResponse

from .schema import RespContent


def response_success(
    *,
    message: str = "success",
    data: t.List | t.Dict | BaseModel | None = None,
) -> JsonResponse:
    data = data or {}
    if isinstance(data, BaseModel):
        data = data.model_dump(exclude_none=True, by_alias=True)
    return JsonResponse(RespContent(data=data, message=message))


def response_error(
    *,
    code: int,
    message: str,
    data: t.List | t.Dict | BaseModel | None = None,
) -> JsonResponse:
    data = data or {}
    if isinstance(data, BaseModel):
        data = data.model_dump(exclude_none=True, by_alias=True)
    return JsonResponse(RespContent(code=code, message=message, data=data))
