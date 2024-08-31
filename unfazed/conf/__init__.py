import typing as t

from pydantic import BaseModel

from unfazed.schema import Cache, Database
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


__all__ = ["UnfazedSettings", "settings"]
