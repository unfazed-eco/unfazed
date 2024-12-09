import typing as t

from pydantic import BaseModel, Field

from unfazed.schema import Cache, Database, OpenAPI
from unfazed.type import CanBeImported

from .base import settings


class UnfazedSettings(BaseModel):
    INSTALLED_APPS: t.List[CanBeImported] = []
    MIDDLEWARE: t.List[CanBeImported] = []
    DEBUG: bool = True
    ROOT_URLCONF: str | None = None
    PROJECT_NAME: str = Field(default="Unfazed")
    DATABASE: Database | None = None
    CACHE: t.Dict[str, Cache] | None = None
    LOGGING: t.Dict[str, t.Any] | None = None
    LIFESPAN: t.Sequence[str] | None = None
    OPENAPI: OpenAPI | None = None
    VERSION: str = Field(default="0.0.1")


__all__ = ["UnfazedSettings", "settings"]
