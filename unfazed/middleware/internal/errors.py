import typing as t

from asgiref import typing as at
from starlette.middleware.errors import ServerErrorMiddleware as _M

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed


class ServerErrorMiddleware(_M):
    def __init__(self, unfazed: "Unfazed", app: at.ASGIApplication):
        self.unfazed = unfazed
        debug = unfazed.settings.DEBUG

        super().__init__(app, debug=debug)
