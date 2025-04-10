from starlette.middleware.gzip import GZipMiddleware as StarletteGZipMiddleware

from unfazed.conf import UnfazedSettings, settings
from unfazed.type import ASGIApp


class GZipMiddleware(StarletteGZipMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        unfazed_settings: UnfazedSettings = settings["UNFAZED_SETTINGS"]
        gzip = unfazed_settings.GZIP

        if not gzip:
            raise ValueError("GZIP settings not found")

        super().__init__(
            app=app,
            minimum_size=gzip.minimum_size,
            compresslevel=gzip.compress_level,
        )
