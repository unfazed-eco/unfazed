import asyncio
import typing as t

import pytest

from unfazed.command import BaseCommand
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_command_center",
    "ROOT_URLCONF": "tests.apps.cmd.routes",
}


def test_command_center() -> None:
    _SETTINGS = {
        **SETTINGS,
        "INSTALLED_APPS": ["tests.apps.cmd.common"],
    }
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_SETTINGS))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(unfazed.setup())

    command_center = unfazed.command_center
    assert "common" in command_center.commands
    assert "_ignore" not in command_center.commands
    assert "sync-common" in command_center.commands

    cmd = t.cast(BaseCommand, command_center.commands["common"])

    loop.call_soon(cmd._callback())  # type: ignore

    cmd = t.cast(BaseCommand, command_center.commands["sync-common"])
    loop.call_soon(cmd._callback())  # type: ignore


async def test_cmd_failed() -> None:
    _SETTINGS = {
        **SETTINGS,
        "INSTALLED_APPS": ["tests.apps.cmd.failed"],
    }
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_SETTINGS))
    with pytest.raises(TypeError):
        await unfazed.setup()


async def test_cli_cmd() -> None:
    unfazed = Unfazed()
    await unfazed.setup_cli()

    assert "startproject" in unfazed.cli_command_center.commands
    assert "_ignore" not in unfazed.cli_command_center.commands
