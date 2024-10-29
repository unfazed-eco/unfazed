from unfazed.conf import settings

from .schema import LoginCtx
from .settings import UnfazedContribAuthSettings


class UserService:
    @classmethod
    def get_settings(cls) -> UnfazedContribAuthSettings:
        return settings["UNFAZED_CONTRIB_AUTH_SETTINGS"]

    @classmethod
    def login(cls, ctx: LoginCtx):
        auth_settings = cls.get_settings()

    @classmethod
    def logout(cls):
        pass
