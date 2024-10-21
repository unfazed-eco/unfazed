from pydantic import BaseModel


class AccountQuery(BaseModel):
    page: int
    size: int
    search: str


class AccountCreate(BaseModel):
    username: str
    email: str


class AccountUpdate(BaseModel):
    username: str
    email: str


class AccountDelete(BaseModel):
    username: str


# cookie
class AccountCookie(BaseModel):
    token: str
    auth: str


# header
class AccountHeader(BaseModel):
    agent: str
    refer: str


# path
class AccountPath(BaseModel):
    user_id: int
