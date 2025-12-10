import mimetypes
from pathlib import Path
from typing import Union

from starlette._utils import get_route_path

from unfazed.exception import MethodNotAllowed
from unfazed.http import FileResponse
from unfazed.http.response import HtmlResponse
from unfazed.type import PathLike, Receive, Scope, Send

# Use tuple for immutable constants
ALLOWED_METHODS = ("GET", "HEAD")
ONE_DAY = 60 * 60 * 24
ONE_MEGABYTE = 1024 * 1024


class StaticFiles:
    def __init__(self, *, directory: PathLike, html: bool = False) -> None:
        # Use Path object directly for directory checks
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileExistsError(f"Directory '{directory}' does not exist")
        if not directory_path.is_dir():
            raise ValueError(f"'{directory}' is not a directory")
        self.directory = directory_path
        self.html = html
        self.html_index = "index.html"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            raise ValueError("StaticFiles can only be used with HTTP requests")

        if scope["method"] not in ALLOWED_METHODS:
            raise MethodNotAllowed()

        path: Path = self.lookup_path(scope)
        is_html: bool = path.name.endswith(self.html_index)

        response = self.get_response(path, is_html)
        await response(scope, receive, send)

    def get_response(
        self, path: Path, html: bool = False
    ) -> Union[FileResponse, HtmlResponse]:
        if html:
            return HtmlResponse(path.read_text(encoding="utf-8"))
        media_type = mimetypes.guess_type(path.name)[0]
        if media_type is None:
            media_type = "text/plain"
        return FileResponse(path, media_type=media_type)

    def lookup_path(self, scope: Scope) -> Path:
        # Combine path operations
        path: str = get_route_path(scope).lstrip("/")
        full_path: Path = (self.directory / path).resolve()

        # Check for index.html only if needed
        if self.html:
            if full_path.is_dir():
                full_path = (full_path / self.html_index).resolve()

            if not full_path.exists():
                fallback = (self.directory / self.html_index).resolve()
                if fallback.exists():
                    full_path = fallback
                else:
                    raise FileNotFoundError(f"File '{full_path}' does not exist")
        else:
            if not full_path.exists():
                raise FileNotFoundError(f"File '{full_path}' does not exist")

        return full_path
