import typing as t

from pydantic import BaseModel

from unfazed.contrib.common.schema import BaseResponse


class LoginCtx(BaseModel):
    account: str = ""
    password: str = ""

    # for most oauth login
    platform: str = "default"

    extra: t.Dict[str, t.Any] = {}


class Role(BaseModel):
    id: int
    name: str


class Group(BaseModel):
    id: int
    name: str


class UserInfo(BaseModel):
    account: str
    email: str
    roles: t.List[Role]
    groups: t.List[Group]
    extra: t.Dict[str, t.Any] | None = None


class LoginSucceedResponse(BaseResponse[UserInfo]):
    pass


class LogoutSucceedResponse(BaseResponse[t.Dict]):
    pass


class RegisterCtx(BaseModel):
    account: str = ""
    password: str = ""

    platform: str = "default"
    extra: t.Dict[str, t.Any] = {}


class RegisterSucceedResponse(BaseResponse[t.Dict]):
    pass


class RedirectUrlCtx(BaseModel):
    redirect_url: str


class RedirectUrlResponse(BaseResponse[RedirectUrlCtx]):
    pass
