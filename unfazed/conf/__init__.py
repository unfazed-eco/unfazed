from pydantic import BaseModel

from unfazed.schema import Database
from unfazed.type import InstalledApps, Middlewares

from .base import settings


class UnfazedSettings(BaseModel):
    INSTALLED_APPS: InstalledApps = []
    MIDDLEWARE: Middlewares = []
    DEBUG: bool = True
    ROOT_URLCONF: str | None = None
    PROJECT_NAME: str | None = None
    DATABASE: Database | None = None


__all__ = ["UnfazedSettings", "settings"]
