import typing as t

from pydantic import BaseModel

from unfazed.conf import register_settings
from unfazed.type import CanBeImported, Doc


class AuthBackend(BaseModel):
    BACKEND_CLS: t.Annotated[
        CanBeImported,
        Doc(
            description="backend class, must inherit from unfazed.contrib.auth.backends.base.BaseAuthBackend",
            examples=["unfazed.contrib.auth.backends.default.DefaultAuthBackend"],
        ),
    ]
    OPTIONS: t.Dict[str, t.Any] = {}


@register_settings("UNFAZED_CONTRIB_AUTH_SETTINGS")
class UnfazedContribAuthSettings(BaseModel):
    """
    example:

    UNFAZED_CONTRIB_AUTH_SETTINGS = {
        "USER_MODEL": "unfazed.contrib.auth.models.User",
        "BACKENDS": {
            "default": {
                "BACKEND_CLS": "unfazed.contrib.auth.backends.default.DefaultAuthBackend",
                "OPTIONS": {}
    }

    """

    USER_MODEL: t.Annotated[
        CanBeImported,
        Doc(description="user model", examples=["unfazed.contrib.auth.models.User"]),
    ]
    BACKENDS: t.Dict[str, AuthBackend] = {}
    SESSION_KEY: str = "unfazed_auth_session"
