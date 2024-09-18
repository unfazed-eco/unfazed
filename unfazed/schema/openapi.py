import typing as t

from pydantic import BaseModel

from unfazed.type import Domain


class OpenAPI(BaseModel):
    servers: t.List[Domain]
