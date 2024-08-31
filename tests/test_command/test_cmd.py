import typing as t

import pytest
from starlette.concurrency import run_in_threadpool

from tests.decorators import mock_unfazed_settings
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_command_center",
    "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
    "ROOT_URLCONF": "tests.apps.cmd.routes",
}


@pytest.mark.asyncio
@mock_unfazed_settings(
    UnfazedSettings(**SETTINGS, INSTALLED_APPS=["tests.apps.cmd.common"])
)
async def test_cmd_common(mocker: "MockerFixture") -> None:
    unfazed = Unfazed()
    await unfazed.setup()
    assert "common" in unfazed.command_center.commands
    assert "_ignore" not in unfazed.command_center.commands
    cmd = unfazed.command_center.commands["common"]
    await run_in_threadpool(cmd._callback)


@pytest.mark.asyncio
@mock_unfazed_settings(
    UnfazedSettings(**SETTINGS, INSTALLED_APPS=["tests.apps.cmd.wrong"])
)
async def test_cmd_noasync(mocker: "MockerFixture") -> None:
    # 1、test if handle method is not a coroutine
    unfazed = Unfazed()
    await unfazed.setup()
    with pytest.raises(TypeError):
        cmd = unfazed.command_center.commands["noasync"]
        cmd._callback()


@pytest.mark.asyncio
@mock_unfazed_settings(
    UnfazedSettings(**SETTINGS, INSTALLED_APPS=["tests.apps.cmd.wrong"])
)
async def test_cmd_wrong(mocker: "MockerFixture") -> None:
    # 2、test if handle method exists
    unfazed = Unfazed()
    await unfazed.setup()
    with pytest.raises(NotImplementedError):
        cmd = unfazed.command_center.commands["nohandle"]
        await cmd.handle()


@pytest.mark.asyncio
@mock_unfazed_settings(
    UnfazedSettings(**SETTINGS, INSTALLED_APPS=["tests.apps.cmd.failed"])
)
async def test_cmd_failed(mocker: "MockerFixture") -> None:
    # 3、test if Command is not a subclass of BaseCommand
    unfazed = Unfazed()
    with pytest.raises(TypeError):
        await unfazed.setup()
