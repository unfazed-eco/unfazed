import typing as t

from pydantic import BaseModel

from unfazed.type import CanBeImported


class Cache(BaseModel):
    BACKEND: CanBeImported
    LOCATION: t.List[str] | str | None = None
    OPTIONS: t.Dict[str, t.Any] = {}
