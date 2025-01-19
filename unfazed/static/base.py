import errno
import os
import typing as t

from starlette._utils import get_route_path
from starlette.datastructures import Headers
from starlette.types import Receive, Scope, Send

from unfazed.exception import MethodNotAllowed, PermissionDenied
from unfazed.http import HttpResponse

PathLike = t.Union[str, "os.PathLike[str]"]


class StaticFiles:
    def __init__(
        self,
        *,
        directory: PathLike,
        html: bool = False,
        follow_symlink: bool = True,
        cached: bool = False,
        cached_alias: str | None = None,
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

    def get_response(self, path: str, scope: Scope) -> HttpResponse:
        try:
            full_path, stat_result = self.lookup_path(path)
        except PermissionError:
            raise PermissionDenied()
        except OSError as exc:
            # Filename is too long, so it can't be a valid static file.
            if exc.errno == errno.ENAMETOOLONG:
                raise ValueError(f"File name too long: {path}")

            raise exc

    def lookup_path(self, path: str) -> str | None:
        joined_path = os.path.join(self.directory, path)
        if self.follow_symlink:
            full_path = os.path.abspath(joined_path)
        else:
            full_path = os.path.realpath(joined_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File '{full_path}' does not exist")

        return full_path, os.stat(full_path)

    def is_not_modified(
        self, response_headers: Headers, request_headers: Headers
    ) -> bool:
        """
        Given the request and response headers, return `True` if an HTTP
        "Not Modified" response could be returned instead.
        """
        try:
            if_none_match = request_headers["if-none-match"]
            etag = response_headers["etag"]
            if etag in [tag.strip(" W/") for tag in if_none_match.split(",")]:
                return True
        except KeyError:
            pass

        try:
            if_modified_since = parsedate(request_headers["if-modified-since"])
            last_modified = parsedate(response_headers["last-modified"])
            if (
                if_modified_since is not None
                and last_modified is not None
                and if_modified_since >= last_modified
            ):
                return True
        except KeyError:
            pass

        return False
