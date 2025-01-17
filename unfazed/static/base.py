import os
import typing as t

from starlette.types import Receive, Scope, Send

PathLike = t.Union[str, "os.PathLike[str]"]


class StaticFiles:
    def __init__(
        self,
        *,
        directory: PathLike,
        packages: t.List[str] | None = None,
        html: bool = False,
        follow_symlink: bool = True,
        cached: bool = False,
    ) -> None:
        if not os.path.exists(directory):
            raise RuntimeError(f"Directory '{directory}' does not exist")
        if not os.path.isdir(directory):
            raise RuntimeError(f"'{directory}' is not a directory")
        self.directory = directory
        self.packages = packages
        self.html = html
        self.follow_symlink = follow_symlink
        self.cached = cached

    def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        pass
