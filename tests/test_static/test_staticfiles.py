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
    with pytest.raises(FileNotFoundError):
        static_files2.lookup_path({"type": "http", "path": "dashboard"})

    static_files_spa = StaticFiles(
        directory=static_dir,
        html=True,
        fallback="index.html",
    )
    path4 = static_files_spa.lookup_path({"type": "http", "path": "dashboard"})
    assert path4 == Path(os.path.join(static_dir, "index.html")).resolve()

    with pytest.raises(FileNotFoundError):
        static_files_spa.lookup_path({"type": "http", "path": "js/missing.js"})

    static_files3 = StaticFiles(directory="/tmp/symlink_static", html=True)
    path5 = static_files3.lookup_path(scope1)
    assert path5 == Path(os.path.join(static_dir, "js/foo.js")).resolve()

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


def test_staticfiles_html_directory_lookup(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    nested_dir = site_dir / "nested"
    nested_dir.mkdir()
    (nested_dir / "index.html").write_text("nested", encoding="utf-8")

    static_files = StaticFiles(directory=site_dir, html=True)

    path_dir = static_files.lookup_path({"type": "http", "path": "nested"})
    assert path_dir == (nested_dir / "index.html").resolve()


def test_staticfiles_html_directory_missing_index(tmp_path: Path) -> None:
    no_index_dir = tmp_path / "no_index"
    no_index_dir.mkdir()
    (no_index_dir / "index.html").write_text("root", encoding="utf-8")
    (no_index_dir / "nested").mkdir()

    static_files_no_index = StaticFiles(directory=no_index_dir, html=True)
    with pytest.raises(FileNotFoundError):
        static_files_no_index.lookup_path({"type": "http", "path": "nested"})


async def test_staticfiles_404_page_and_path_traversal(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "404.html").write_text("missing", encoding="utf-8")

    static_files = StaticFiles(directory=site_dir, html=True)
    events: list[t.MutableMapping[str, t.Any]] = []

    async def mock_receive() -> t.Dict[str, str]:
        return {"type": "http.disconnect"}

    async def mock_send(message: t.MutableMapping[str, t.Any]) -> None:
        events.append(message)

    await static_files(
        {"type": "http", "method": "GET", "path": "missing"},
        mock_receive,
        mock_send,
    )

    assert events[0]["status"] == 404
    assert b"missing" in events[1]["body"]

    with pytest.raises(FileNotFoundError):
        static_files.lookup_path({"type": "http", "path": "../secret.txt"})


def test_staticfiles_unknown_media_type(tmp_path: Path) -> None:
    """Test that files with unknown extensions get text/plain as media_type"""
    # Create a test directory with a file without extension
    test_dir = tmp_path / "test"
    test_dir.mkdir()

    # Create a file without extension (mimetype will be None)
    unknown_file = test_dir / "README"
    unknown_file.write_text("test content", encoding="utf-8")

    static_files = StaticFiles(directory=test_dir)

    # Test get_response with unknown file type
    response = static_files.get_response(unknown_file, html=False)

    # Verify that the media_type is set to text/plain for unknown types
    assert response.media_type == "text/plain"


def test_staticfiles_invalid_fallback(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()

    with pytest.raises(FileExistsError):
        StaticFiles(directory=site_dir, html=True, fallback="index.html")

    fallback_dir = site_dir / "fallback"
    fallback_dir.mkdir()

    with pytest.raises(ValueError):
        StaticFiles(directory=site_dir, html=True, fallback="fallback")
