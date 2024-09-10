import asyncio
import typing as t
from unittest.mock import patch

import pytest

from tests.decorators import mock_unfazed_settings
from unfazed.app import AppCenter
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


_Setting = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_launch",
    "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
    "ROOT_URLCONF": "tests.apps.core.routes",
    "INSTALLED_APPS": ["tests.apps.core.common"],
    "LOGGING": {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # Default is stderr
            },
        },
        "loggers": {
            "common": {  # root logger
                "handlers": ["default"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    },
}

Setting = UnfazedSettings(**_Setting)


@pytest.mark.asyncio
@mock_unfazed_settings(Setting)
async def test_app_launch(mocker: "MockerFixture") -> None:
    unfazed = Unfazed()

    await unfazed.setup()

    assert unfazed.ready is True
    # test repeated setup
    await unfazed.setup()
    assert unfazed.ready is True


@pytest.mark.asyncio
@mock_unfazed_settings(Setting)
async def test_loading_state(mocker: "MockerFixture") -> None:
    unfazed = Unfazed()

    # test loading state
    async def new_app_center_setup(self):
        await asyncio.sleep(1)

    with patch.object(AppCenter, "setup", new=new_app_center_setup):
        with pytest.raises(RuntimeError):
            await asyncio.gather(unfazed.setup(), unfazed.setup())
