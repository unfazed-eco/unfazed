import typing as t

import pytest
from starlette.concurrency import run_in_threadpool

from unfazed.command import BaseCommand
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_command_center",
    "ROOT_URLCONF": "tests.apps.cmd.routes",
}


async def test_cmd_common() -> None:
    _SETTINGS = {
        **SETTINGS,
        "INSTALLED_APPS": ["tests.apps.cmd.common"],
    }
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_SETTINGS))
    await unfazed.setup()
    assert "common" in unfazed.command_center.commands
    assert "_ignore" not in unfazed.command_center.commands
    cmd: BaseCommand = unfazed.command_center.commands["common"]
    await run_in_threadpool(cmd._callback)


async def test_cmd_noasync() -> None:
    # 1、test if handle method is not a coroutine
    _SETTINGS = {
        **SETTINGS,
        "INSTALLED_APPS": ["tests.apps.cmd.wrong"],
    }
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_SETTINGS))
    await unfazed.setup()
    with pytest.raises(TypeError):
        cmd: BaseCommand = unfazed.command_center.commands["noasync"]
        cmd._callback()


async def test_cmd_wrong(mocker: "MockerFixture") -> None:
    # 2、test if handle method exists
    _SETTINGS = {
        **SETTINGS,
        "INSTALLED_APPS": ["tests.apps.cmd.wrong"],
    }
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_SETTINGS))
    await unfazed.setup()
    with pytest.raises(NotImplementedError):
        cmd: BaseCommand = unfazed.command_center.commands["nohandle"]
        await cmd.handle()


async def test_cmd_failed(mocker: "MockerFixture") -> None:
    # 3、test if Command is not a subclass of BaseCommand

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
