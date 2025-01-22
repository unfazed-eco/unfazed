import os
from pathlib import Path

from starlette._utils import get_route_path
from starlette.types import Receive, Scope, Send

from unfazed.exception import MethodNotAllowed
from unfazed.http import FileResponse
from unfazed.type import PathLike

ONE_DAY = 60 * 60 * 24
ONE_MEGABYTE = 1024 * 1024


class StaticFiles:
    def __init__(self, *, directory: PathLike, html: bool = False) -> None:
        if not os.path.exists(directory):
            raise FileExistsError(f"Directory '{directory}' does not exist")
        if not os.path.isdir(directory):
            raise ValueError(f"'{directory}' is not a directory")
        self.directory = Path(directory)
        self.html = html

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            raise ValueError("StaticFiles can only be used with HTTP requests")

        if scope["method"] not in ("GET", "HEAD"):
            raise MethodNotAllowed()

        path = self.lookup_path(scope)
        response = self.get_response(path)
        await response(scope, receive, send)

    def get_response(self, path: Path) -> FileResponse:
        return FileResponse(path)

    def lookup_path(self, scope: Scope) -> Path:
        path = get_route_path(scope)
        path = path.lstrip("/")
        joined_path = self.directory / path

        full_path = joined_path.resolve()

        if not full_path.exists() and self.html:
            joined_path = self.directory / "index.html"
            full_path = joined_path.resolve()

        if not full_path.exists():
            raise FileNotFoundError(f"File '{full_path}' does not exist")

        return full_path
