import typing as t

from pydantic import BaseModel, Field

T = t.TypeVar("T", bound=t.Union[BaseModel, t.Dict, t.List])


class BaseResponse(BaseModel, t.Generic[T]):
    code: int = Field(
        default=0, description="response code, 0 for success, other for error"
    )
    message: str = Field(default="success", description="response message")
    data: T | t.Dict[str, t.Any] = Field(default={}, description="response data")


class ErrorResponse(BaseResponse[t.Dict[str, t.Any]]):
    code: int = Field(default=500, description="response code, 500 for error")
    message: str = Field(default="error", description="response message")
