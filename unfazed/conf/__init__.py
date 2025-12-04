import typing as t

from pydantic import BaseModel, Field

from unfazed.schema import (
    Cache,
    Cors,
    Database,
    GZip,
    OpenAPI,
    TrustedHost,
)
from unfazed.type import CanBeImported

from .base import settings
from .decorators import register_settings


@register_settings("UNFAZED_SETTINGS")
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
    CORS: Cors | None = None
    TRUSTED_HOST: TrustedHost | None = None
    GZIP: GZip | None = None


__all__ = ["UnfazedSettings", "settings", "register_settings"]
