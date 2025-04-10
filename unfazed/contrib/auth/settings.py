import typing as t

from pydantic import BaseModel

from unfazed.conf import register_settings
from unfazed.type import CanBeImported


class AuthBackend(BaseModel):
    BACKEND_CLS: str
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

    USER_MODEL: CanBeImported
    BACKENDS: t.Dict[str, AuthBackend] = {}
    SESSION_KEY: str = "unfazed_auth_session"
