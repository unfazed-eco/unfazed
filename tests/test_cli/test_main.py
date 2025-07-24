import os
import typing as t
from unittest.mock import patch

import pytest

from unfazed.cli import import_unfazed, main
from unfazed.conf import settings
from unfazed.core import Unfazed


@pytest.fixture(autouse=True)
def setup_cli_env() -> t.Generator[None, None, None]:
    settings.clear()

    yield


def test_main() -> None:
    with patch("unfazed.command.CliCommandCenter.main") as main_func:
        main_func.return_value = None
        main()
        assert main_func.call_count == 1

    with patch("os.getcwd") as getcwd_func:
        getcwd_func.return_value = os.path.join(
            os.path.dirname(__file__), "proj/src/backend"
        )
        with patch("unfazed.command.CommandCenter.main") as main_func:
            main_func.return_value = None
            main()
            assert main_func.call_count == 1


async def test_import_unfazed() -> None:
    asgi_path = os.path.join(os.path.dirname(__file__), "proj/src/backend")

    app = import_unfazed(asgi_path)

    assert isinstance(app, Unfazed)

    wrong_asgi_path = os.path.join(os.path.dirname(__file__), "proj/src")
    app = import_unfazed(wrong_asgi_path)
    assert app is None
