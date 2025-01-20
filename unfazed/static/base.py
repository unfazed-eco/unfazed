import errno
import os
import typing as t

from starlette._utils import get_route_path
from starlette.types import Receive, Scope, Send

from unfazed.exception import MethodNotAllowed, PermissionDenied
from unfazed.http import FileResponse

PathLike = t.Union[str, "os.PathLike[str]"]

ONE_DAY = 60 * 60 * 24
ONE_MEGABYTE = 1024 * 1024


class StaticFiles:
    def __init__(
        self,
        *,
        directory: PathLike,
        html: bool = False,
        follow_symlink: bool = True,
        cached: bool = False,
        cached_alias: str | None = None,
        cached_timeout: int = ONE_DAY,
        cached_max_size: int = ONE_MEGABYTE,
    ) -> None:
        if not os.path.exists(directory):
            raise FileExistsError(f"Directory '{directory}' does not exist")
        if not os.path.isdir(directory):
            raise ValueError(f"'{directory}' is not a directory")
        self.directory = directory
        self.html = html
        self.follow_symlink = follow_symlink
        self.cached = cached
        self.cached_alias = cached_alias
        self.cached_timeout = cached_timeout
        self.cached_max_size = cached_max_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            raise ValueError("StaticFiles can only be used with HTTP requests")

        if scope["method"] not in ("GET", "HEAD"):
            raise MethodNotAllowed()

        path = self.get_path(scope)
        response = await self.get_response(path, scope)
        await response(scope, receive, send)

    def get_path(self, scope: Scope) -> str:
        route_path = get_route_path(scope)
        return os.path.normpath(os.path.join(*route_path.split("/")))

    def get_response(self, path: str, scope: Scope) -> FileResponse:
        try:
            full_path, stat_result = self.lookup_path(path)
        except PermissionError:
            raise PermissionDenied()
        except OSError as exc:
            # Filename is too long, so it can't be a valid static file.
            if exc.errno == errno.ENAMETOOLONG:
                raise ValueError(f"File name too long: {path}")

            raise exc

        return FileResponse(full_path)

    def lookup_path(self, path: str) -> t.Tuple[str, os.stat_result]:
        joined_path = os.path.join(self.directory, path)
        if self.follow_symlink:
            full_path = os.path.abspath(joined_path)
        else:
            full_path = os.path.realpath(joined_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File '{full_path}' does not exist")

        return full_path, os.stat(full_path)
