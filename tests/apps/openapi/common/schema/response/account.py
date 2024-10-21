import typing as t
from enum import Enum

from pydantic import BaseModel

from unfazed.route.params import ResponseSpec


class AccountStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Account(BaseModel):
    user_name: str
    email: str
    status: AccountStatus


class _BaseResp(BaseModel):
    code: int
    message: str


class _QueryResp(_BaseResp):
    data: t.List[Account]


SuccessfulQueryResp = ResponseSpec(code="200", model=_QueryResp)
FailedResp = ResponseSpec(code="400", model=_BaseResp, description="Bad Request")


class _CreateResp(_BaseResp):
    data: Account


SuccessfulCreateResp = ResponseSpec(code="200", model=_CreateResp)


class _UpdateResp(_BaseResp):
    data: Account


SuccessfulUpdateResp = ResponseSpec(code="200", model=_CreateResp)

SuccessfulDeleteResp = ResponseSpec(code="200", model=_BaseResp)
