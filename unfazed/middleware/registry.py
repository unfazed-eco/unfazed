import typing as t
from threading import Lock

from starlette.middleware import Middleware

from unfazed.utils.module_loading import import_string


class MiddleWareCenter:
    def __init__(self, middleware_paths: list[str] = None) -> None:
        self._middleware_paths = middleware_paths or []
        self._ready = False
        self._lock = Lock()
        self.middlewares: t.Sequence[Middleware] = []

    def setup(self) -> None:
        if self._ready:
            return

        with self._lock:
            if self._ready:
                return
            for middleware_path in self._middleware_paths:
                middleware_cls = import_string(middleware_path)
                self.middlewares.append(middleware_cls)

        return None
