import asyncio
import os
import typing as t
from unittest.mock import patch

import pytest

from unfazed.app import AppCenter
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed
from unfazed.lifespan import lifespan_handler

HOST = os.getenv("REDIS_HOST", "redis")

_Setting = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_launch",
    "ROOT_URLCONF": "tests.apps.core.routes",
    "INSTALLED_APPS": ["tests.apps.core.common"],
    "MIDDLEWARE": ["tests.apps.core.middleware.set_session.SetSessionMiddleware"],
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
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.redis.SerializerBackend",
            "LOCATION": f"redis://{HOST}:6379",
        },
    },
    "LIFESPAN": ["tests.apps.core.lifespan.set_count.SetCount"],
    "OPENAPI": {
        "servers": [{"url": "http://127.0.0.1:9527", "description": "Local"}],
    },
    "VERSION": "0.1.0",
}

Setting = UnfazedSettings.model_validate(_Setting)


async def test_app_launch() -> None:
    unfazed = Unfazed(settings=Setting)

    await unfazed.setup()

    assert unfazed.ready is True
    # test repeated setup
    await unfazed.setup()
    assert unfazed.ready is True


async def test_failed_unfazed() -> None:
    unfazed = Unfazed(settings=Setting)

    # test loading state
    async def new_app_center_setup(self: t.Any) -> None:
        await asyncio.sleep(1)

    with patch.object(AppCenter, "setup", new=new_app_center_setup):
        with pytest.raises(RuntimeError):
            await asyncio.gather(unfazed.setup(), unfazed.setup())

    # test failed lifespan
    new_settings = Setting.model_copy()
    new_settings.LIFESPAN = ["tests.apps.core.lifespan.failed.Failed"]

    with pytest.raises(ValueError):
        unfazed = Unfazed(settings=new_settings)
        await unfazed.setup()


async def test_cliapp_launch() -> None:
    unfazed = Unfazed(settings=Setting)

    await unfazed.setup_cli()
    assert unfazed.ready is True

    await unfazed.setup_cli()
    assert unfazed.ready is True


async def test_execute_command() -> None:
    unfazed = Unfazed(settings=Setting)
    lifespan_handler.clear()

    await unfazed.setup()

    with patch("unfazed.command.CliCommandCenter.main") as main:
        main.return_value = None
        await unfazed.execute_command_from_cli()
        assert main.call_count == 1

    with patch("unfazed.command.CommandCenter.main") as main:
        main.return_value = None
        await unfazed.execute_command_from_argv()
        assert main.call_count == 1
