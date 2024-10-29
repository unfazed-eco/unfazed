import typing as t

from pydantic import BaseModel

from unfazed.type import CanBeImported



class Session(BaseModel):

    BACKEND: CanBeImported = "unfazed.contrib.auth.backends.SessionBackend"

class UnfazedContribAuthSettings(BaseModel):
    AUTH_USER: CanBeImported
    LOGIN_PLUGINS: t.List[CanBeImported] = []
