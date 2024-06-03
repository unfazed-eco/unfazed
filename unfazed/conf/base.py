import importlib
import os
import typing as t

from pydantic import BaseModel
from unfazed.const import UNFAZED_SETTINGS_MODULE
from unfazed.types import InstalledApp, Middlewares


def get_settings_module() -> t.Mapping:
    settings_module = os.environ.get(UNFAZED_SETTINGS_MODULE)
    if not settings_module:
        raise Exception("UNFAZED_SETTINGS_MODULE environment variable is not set")
    try:
        settingskv = importlib.import_module(settings_module).__dict__
    except ImportError:
        raise ImportError(f"Could not import settings module {settings_module}")

    return settingskv


class BaseSettings(BaseModel):
    INSTALLED_APPS: InstalledApp
    MIDDLEWARE: Middlewares
    DEBUG: bool
    ROOT_URLCONF: str
    DATABASE: t.Mapping | None = None
    PROJECT_NAME: str

    @classmethod
    def setup(cls):
        # get all key-value settings from the settings module
        return cls(**get_settings_module())


def settings_from_key(key: str) -> t.Mapping:
    settings_kv = get_settings_module()

    if key not in settings_kv:
        raise KeyError(f"{key} is not found in settings module")

    return settings_kv[key]
