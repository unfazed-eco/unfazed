import mimetypes
from pathlib import Path
from typing import Union

from starlette._utils import get_route_path

from unfazed.exception import MethodNotAllowed
from unfazed.http import FileResponse
from unfazed.http.response import HtmlResponse
from unfazed.type import PathLike, Receive, Scope, Send

ALLOWED_METHODS = ("GET", "HEAD")


class StaticFiles:
    """
    Serve static files from a directory.

    Args:
        directory: The directory to serve files from.
        html: Whether to serve HTML files.
        fallback: The fallback file to serve for missing route-like paths.
    """

    def __init__(
        self,
        *,
        directory: PathLike,
        html: bool = False,
        fallback: str | None = None,
    ) -> None:
        directory_path = Path(directory).resolve()
        if not directory_path.exists():
            raise FileExistsError(f"Directory '{directory}' does not exist")
        if not directory_path.is_dir():
            raise ValueError(f"'{directory}' is not a directory")
        self.directory = directory_path
        self.html = html
        self.fallback = fallback
        self.html_index = "index.html"
        if fallback is not None:
            self._validate_fallback(fallback)

    def _validate_fallback(self, fallback: str) -> None:
        """
        Validate the fallback file.

        Args:
            fallback: The fallback file to validate.
        """
        fallback_path = self._resolve_relative_path(fallback)
        if not fallback_path.exists():
            raise FileExistsError(f"Fallback file '{fallback}' does not exist")
        if not fallback_path.is_file():
            raise ValueError(f"Fallback '{fallback}' is not a file")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Serve the static files.

        Args:
            scope: The scope of the request.
            receive: The receive function.
            send: The send function.
        """
        if scope["type"] != "http":
            raise ValueError("StaticFiles can only be used with HTTP requests")

        if scope["method"] not in ALLOWED_METHODS:
            raise MethodNotAllowed()

        path, status_code = self.resolve_path(scope)
        is_html: bool = path.suffix.lower() == ".html"

        response = self.get_response(path, is_html, status_code=status_code)
        await response(scope, receive, send)

    def get_response(
        self, path: Path, html: bool = False, status_code: int = 200
    ) -> Union[FileResponse, HtmlResponse]:
        """
        Get the response for the path.

        Args:
            path: The path to get the response for.
            html: Whether the path is an HTML file.
            status_code: The status code to use for the response.
        """
        if html:
            return HtmlResponse(
                path.read_text(encoding="utf-8"), status_code=status_code
            )
        media_type = mimetypes.guess_type(path.name)[0]
        if media_type is None:
            media_type = "text/plain"
        return FileResponse(path, media_type=media_type, status_code=status_code)

    def resolve_path(self, scope: Scope) -> tuple[Path, int]:
        """
        Resolve the path from the directory.

        Args:
            scope: The scope of the request.
        """
        path = get_route_path(scope).lstrip("/")
        resolved = self._lookup_existing_path(path)
        if resolved is not None:
            return resolved, 200

        route_like = self._is_route_like_path(path)

        if self.fallback is not None and route_like:
            return self._resolve_relative_path(self.fallback), 200

        if self.html and route_like:
            not_found = self._lookup_existing_path("404.html")
            if not_found is not None:
                return not_found, 404

        full_path = self._resolve_relative_path(path)
        raise FileNotFoundError(f"File '{full_path}' does not exist")

    def lookup_path(self, scope: Scope) -> Path:
        """
        Lookup the path from the directory.

        Args:
            scope: The scope of the request.
        """
        path, _ = self.resolve_path(scope)
        return path

    def _lookup_existing_path(self, path: str) -> Path | None:
        """
        Lookup the existing path from the directory.

        Args:
            path: The path to lookup.
        """
        full_path = self._resolve_relative_path(path)
        if full_path.is_file():
            return full_path

        if full_path.is_dir() and self.html:
            index_path = self._resolve_relative_path(
                f"{path.rstrip('/')}/{self.html_index}" if path else self.html_index
            )
            if index_path.is_file():
                return index_path

        return None

    def _resolve_relative_path(self, path: str) -> Path:
        """
        Resolve the relative path from the directory.

        Args:
            path: The path to resolve.
        """
        full_path = (self.directory / path.lstrip("/")).resolve()
        if not full_path.is_relative_to(self.directory):
            raise FileNotFoundError(f"File '{full_path}' does not exist")
        return full_path

    def _is_route_like_path(self, path: str) -> bool:
        """Check if the path is a route-like path.

        Args:
            path: The path to check.
        """
        suffix = Path(path).suffix.lower()
        return suffix in ("", ".html")
