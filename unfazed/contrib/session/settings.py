import typing as t

from pydantic import BaseModel, Field

from unfazed.type import CanBeImported


class SessionSettings(BaseModel):
    engine: CanBeImported = Field(
        "unfazed.contrib.session.backend.cache.SessionStore",
        alias="ENGINE",
    )
    cookie_name: str = Field(..., alias="COOKIE_NAME")
    cookie_domain: str = Field(..., alias="COOKIE_DOMAIN")
    cookie_path: str = Field(None, alias="COOKIE_PATH")
    cookie_secure: bool = Field(False, alias="COOKIE_SECURE")
    cookie_httponly: bool = Field(True, alias="COOKIE_HTTPONLY")
    cookie_samesite: t.Literal["lax", "strict", "none"] = Field(
        "lax",
        alias="COOKIE_SAMESITE",
    )
    cookie_max_age: int = Field(60 * 60 * 24 * 7, alias="COOKIE_MAX_AGE")
    cookie_expires: int = Field(None, alias="COOKIE_EXPIRES")
