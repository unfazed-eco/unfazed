import typing as t

from pydantic import BaseModel, Field

from unfazed.conf import register_settings
from unfazed.type import CanBeImported


@register_settings("UNFAZED_CONTRIB_SESSION_SETTINGS")
class SessionSettings(BaseModel):
    # required
    secret_key: str = Field(..., alias="SECRET")

    # require recommended
    cookie_domain: str | None = Field(default=None, alias="COOKIE_DOMAIN")

    engine: CanBeImported = Field(
        default="unfazed.contrib.session.backends.default.SigningSession",
        alias="ENGINE",
    )
    cookie_name: str = Field(default="session_id", alias="COOKIE_NAME")
    cookie_path: str = Field(default="/", alias="COOKIE_PATH")
    cookie_secure: bool = Field(default=False, alias="COOKIE_SECURE")
    cookie_httponly: bool = Field(default=True, alias="COOKIE_HTTPONLY")
    cookie_samesite: t.Literal["lax", "strict", "none"] = Field(
        default="lax",
        alias="COOKIE_SAMESITE",
    )
    cookie_max_age: int = Field(default=60 * 60 * 24 * 7, alias="COOKIE_MAX_AGE")

    # If both Expires and Max-Age are set, Max-Age has precedence.
    # => so unfazed ignore `expires`
    # cookie_expires: int = Field(None, alias="COOKIE_EXPIRES")

    # if you want to use cache session
    # set the cache alias
    cache_alias: str = Field(default="default", alias="CACHE_ALIAS")
