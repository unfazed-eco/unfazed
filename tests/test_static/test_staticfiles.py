import os
import typing as t
from pathlib import Path

import pytest

from unfazed.exception import MethodNotAllowed
from unfazed.static import StaticFiles


@pytest.fixture(autouse=True)
def setup_staticfiles() -> t.Generator[None, None, None]:
    # create a temporary follow symlink directory
    static_dir = os.path.join(os.path.dirname(__file__), "../staticfiles")
    os.symlink(static_dir, "/tmp/symlink_static")

    yield

    # cleanup
    os.remove("/tmp/symlink_static")


async def test_staticfiles_methods() -> None:
    static_dir = os.path.join(os.path.dirname(__file__), "../staticfiles")

    with pytest.raises(FileExistsError):
        StaticFiles(directory=os.path.join(static_dir, "nonexistent"))

    with pytest.raises(ValueError):
        StaticFiles(directory=os.path.join(static_dir, "index.html"))

    static_files = StaticFiles(directory=static_dir)

    scope1 = {"type": "http", "path": "js/foo.js"}
    scope2 = {"type": "http", "path": "css/bar.css"}
    scope3 = {"type": "http", "path": "not_found.html"}

    # test lookup path
    path1 = static_files.lookup_path(scope1)
    assert path1 == Path(os.path.join(static_dir, "js/foo.js")).resolve()

    path2 = static_files.lookup_path(scope2)
    assert path2 == Path(os.path.join(static_dir, "css/bar.css")).resolve()

    with pytest.raises(FileNotFoundError):
        static_files.lookup_path(scope3)

    static_files2 = StaticFiles(directory=static_dir, html=True)
    path3 = static_files2.lookup_path(scope3)
    assert path3 == Path(os.path.join(static_dir, "index.html")).resolve()

    static_files3 = StaticFiles(directory="/tmp/symlink_static", html=True)
    path4 = static_files3.lookup_path(scope1)
    assert path4 == Path(os.path.join(static_dir, "js/foo.js")).resolve()

    # test __call__
    scope4 = {"type": "websocket", "path": "js/foo.js"}

    async def mock_receive() -> t.Dict:
        return {}

    async def mock_send(message: t.Any) -> None:
        pass

    with pytest.raises(ValueError):
        await static_files(scope4, mock_receive, mock_send)

    scope5 = {"type": "http", "method": "POST", "path": "js/foo.js"}
    with pytest.raises(MethodNotAllowed):
        await static_files(scope5, mock_receive, mock_send)
