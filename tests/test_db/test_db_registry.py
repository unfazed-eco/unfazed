import os
import typing as t

import pytest
from tortoise import Tortoise

from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed


@pytest.fixture(autouse=True)
def setup_db_env() -> t.Generator:
    Tortoise.apps = {}
    Tortoise._inited = False

    yield


_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_db",
}


_Settings2 = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_db",
    "INSTALLED_APPS": ["tests.apps.orm.common"],
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.mysql",
                "CREDENTIALS": {
                    "HOST": os.environ.get("MYSQL_HOST", "mysql"),
                    "PORT": int(os.environ.get("MYSQL_PORT", 3306)),
                    "USER": "root",
                    "PASSWORD": "app",
                    "DATABASE": "test_app",
                },
            }
        }
    },
}


async def test_db_registry() -> None:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(_Settings))

    await unfazed.setup()

    assert unfazed.model_center.driver is None

    with pytest.raises(ValueError):
        await unfazed.migrate()

    unfazed2 = Unfazed(settings=UnfazedSettings.model_validate(_Settings2))

    await unfazed2.setup()
    assert unfazed2.model_center.driver is not None

    await unfazed2.migrate()
