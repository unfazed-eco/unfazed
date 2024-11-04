import typing as t

from pydantic import BaseModel

from unfazed.route import params


class LoginCtx(BaseModel):
    account: str = ""
    password: str = ""

    # for most oauth login
    token: str = ""

    extra: t.Dict[str, t.Any] | None = None


class LoginResponse(BaseModel):
    extra: t.Dict[str, t.Any] | None = None


class LoginSucceed(BaseModel):
    msg: str = ""
    code: int = 0
    data: LoginResponse | None = None


class LogoutSucceed(BaseModel):
    msg: str = ""
    code: int = 0


LOGIN_RESPONSE = [params.ResponseSpec(model=LoginSucceed)]
LOUOUT_RESPONSE = [params.ResponseSpec(model=LogoutSucceed)]