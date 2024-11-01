import typing as t

from pydantic import BaseModel, Field

from unfazed.type import CanBeImported


class SessionSettings(BaseModel):
    # required
    secret_key: str = Field(..., alias="SECRET")

    # require recommended
    cookie_domain: str | None = Field(None, alias="COOKIE_DOMAIN")

    engine: CanBeImported = Field(
        "unfazed.contrib.session.backends.default.SigningSession",
        alias="ENGINE",
    )
    cookie_name: str = Field("session_id", alias="COOKIE_NAME")
    cookie_path: str = Field("/", alias="COOKIE_PATH")
    cookie_secure: bool = Field(False, alias="COOKIE_SECURE")
    cookie_httponly: bool = Field(True, alias="COOKIE_HTTPONLY")
    cookie_samesite: t.Literal["lax", "strict", "none"] = Field(
        "lax",
        alias="COOKIE_SAMESITE",
    )
    cookie_max_age: int = Field(60 * 60 * 24 * 7, alias="COOKIE_MAX_AGE")

    # If both Expires and Max-Age are set, Max-Age has precedence.
    # => so unfazed ignore `expires`
    # cookie_expires: int = Field(None, alias="COOKIE_EXPIRES")

    # if you want to use cache session
    # set the cache alias
    cache_alias: str = Field("default", alias="CACHE_ALIAS")
