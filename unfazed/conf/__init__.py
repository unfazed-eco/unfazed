import typing as t

from pydantic import BaseModel

from unfazed.schema import Cache, Database, OpenAPI
from unfazed.type import InstalledApps, Middlewares

from .base import settings


class UnfazedSettings(BaseModel):
    INSTALLED_APPS: InstalledApps = []
    MIDDLEWARE: Middlewares = []
    DEBUG: bool = True
    ROOT_URLCONF: str | None = None
    PROJECT_NAME: str | None = None
    DATABASE: Database | None = None
    CACHE: t.Dict[str, Cache] | None = None
    LOGGING: t.Dict[str, t.Any] | None = None
    LIFESPAN: t.Sequence[str] | None = None
    OPENAPI: OpenAPI | None = None
    VERSION: str | None = None


__all__ = ["UnfazedSettings", "settings"]
