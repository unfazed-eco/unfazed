import typing as t
from threading import Lock

from starlette.applications import Starlette

from unfazed import protocol as p
from unfazed.conf import UnfazedSettings, settings


class Unfazed(Starlette):
    version = "0.0.1"

    def __init__(
        self,
        debug: bool = False,
        routes: t.Sequence[p.Route] | None = None,
        middlewares: t.Sequence[p.MiddleWare] | None = None,
    ) -> None:
        self._ready = False
        super().__init__(debug=debug, routes=routes, middleware=middlewares)

    @property
    def settings(self) -> UnfazedSettings:
        return settings["UNFAZED_SETTINGS"]

    def setup(self) -> None:
        if self._ready:
            return
        with Lock():
            if self._ready:
                return

            self._ready = True
