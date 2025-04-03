from pathlib import Path

from starlette._utils import get_route_path

from unfazed.exception import MethodNotAllowed
from unfazed.http import FileResponse
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

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            raise ValueError("StaticFiles can only be used with HTTP requests")

        if scope["method"] not in ALLOWED_METHODS:
            raise MethodNotAllowed()

        path = self.lookup_path(scope)
        response = self.get_response(path)
        await response(scope, receive, send)

    def get_response(self, path: Path) -> FileResponse:
        return FileResponse(path)

    def lookup_path(self, scope: Scope) -> Path:
        # Combine path operations
        path = get_route_path(scope).lstrip("/")
        full_path = (self.directory / path).resolve()

        # Check for index.html only if needed
        if not full_path.exists() and self.html:
            full_path = (self.directory / "index.html").resolve()

        if not full_path.exists():
            raise FileNotFoundError(f"File '{full_path}' does not exist")

        return full_path
