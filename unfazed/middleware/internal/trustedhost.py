from starlette.middleware.trustedhost import (
    TrustedHostMiddleware as StarletteTrustedHostMiddleware,
)

from unfazed.conf import UnfazedSettings, settings
from unfazed.type import ASGIApp


class TrustedHostMiddleware(StarletteTrustedHostMiddleware):
    """
    TrustedHost Middleware inherit from Starlette TrustedHostMiddleware

    """

    def __init__(self, app: ASGIApp) -> None:
        unfazed_settings: UnfazedSettings = settings["UNFAZED_SETTINGS"]

        trusted_host = unfazed_settings.TRUSTED_HOST

        if not trusted_host:
            raise ValueError("TRUSTED_HOST settings not found")

        super().__init__(
            app=app,
            allowed_hosts=trusted_host.allowed_hosts,
            www_redirect=trusted_host.www_redirect,
        )
