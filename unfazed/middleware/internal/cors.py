from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware

from unfazed.conf import UnfazedSettings, settings
from unfazed.type import ASGIApp


class CORSMiddleware(StarletteCORSMiddleware):
    """
    Cors Middleware inherit from Starlette CORSMiddleware

    """

    def __init__(self, app: ASGIApp) -> None:
        unfazed_settings: UnfazedSettings = settings["UNFAZED_SETTINGS"]
        cors = unfazed_settings.CORS

        if not cors:
            raise ValueError("CORS settings not found")

        super().__init__(
            app=app,
            allow_origins=cors.allow_origins,
            allow_methods=cors.allow_methods,
            allow_headers=cors.allow_headers,
            allow_credentials=cors.allow_credentials,
            allow_origin_regex=cors.allow_origin_regex,
            expose_headers=cors.expose_headers,
            max_age=cors.max_age,
        )
