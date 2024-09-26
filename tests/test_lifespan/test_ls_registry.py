from unittest.mock import PropertyMock, patch

import pytest
from uvicorn.config import Config
from uvicorn.lifespan.on import LifespanOn

from unfazed.conf import UnfazedSettings
from unfazed.core.application import Unfazed
from unfazed.lifespan import lifespan_handler
from unfazed.protocol import BaseLifeSpan


class HelloLifeSpan(BaseLifeSpan):
    def __init__(self, unfazed: Unfazed) -> None:
        self.unfazed = unfazed
        self.count = 1

    async def on_startup(self) -> None:
        self.count += 1

    async def on_shutdown(self) -> None:
        self.count += 1

    @property
    def state(self):
        return {"foo": "bar"}


class HelloLifeSpan2(BaseLifeSpan):
    def __init__(self, unfazed: Unfazed) -> None:
        self.unfazed = unfazed
        self.count = 1

    async def on_startup(self) -> None:
        self.count += 1

    async def on_shutdown(self) -> None:
        self.count += 1

    @property
    def state(self):
        return {}


SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_serializer",
    "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
    "LIFESPAN": [
        "tests.test_lifespan.test_ls_registry.HelloLifeSpan",
    ],
}


@pytest.mark.asyncio
async def test_registry() -> None:
    with patch(
        "unfazed.core.Unfazed.settings",
        new_callable=PropertyMock,
        return_value=UnfazedSettings(**SETTINGS),
    ):
        unfazed = Unfazed()
        lifespan_handler.clear()
        await unfazed.setup()

        hello_life_span = lifespan_handler.get(
            "tests.test_lifespan.test_ls_registry.HelloLifeSpan"
        )

        # use uvicorn to trigger startup and shutdown
        config = Config(app=unfazed)
        uvicorn_ls = LifespanOn(config)

        await uvicorn_ls.startup()
        assert hello_life_span.count == 2

        await uvicorn_ls.shutdown()
        assert hello_life_span.count == 3


SETTINGS2 = {
    "DEBUG": True,
    "PROJECT_NAME": "test_lifespan",
    "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
    "LIFESPAN": [
        "tests.test_lifespan.test_ls_registry.HelloLifeSpan",
        "tests.test_lifespan.test_ls_registry.HelloLifeSpan",
    ],
}


@pytest.mark.asyncio
async def test_failed() -> None:
    with patch(
        "unfazed.core.Unfazed.settings",
        new_callable=PropertyMock,
        return_value=UnfazedSettings(**SETTINGS),
    ):
        unfazed = Unfazed()

        with pytest.raises(ValueError):
            await unfazed.setup()


SETTINGS3 = {
    "DEBUG": True,
    "PROJECT_NAME": "test_lifespan",
    "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
    "LIFESPAN": [
        "tests.test_lifespan.test_ls_registry.HelloLifeSpan2",
    ],
}


@pytest.mark.asyncio
async def test_empty_state() -> None:
    with patch(
        "unfazed.core.Unfazed.settings",
        new_callable=PropertyMock,
        return_value=UnfazedSettings(**SETTINGS3),
    ):
        unfazed = Unfazed()
        lifespan_handler.clear()
        await unfazed.setup()
        hello_life_span = lifespan_handler.get(
            "tests.test_lifespan.test_ls_registry.HelloLifeSpan2"
        )

        # use uvicorn to trigger startup and shutdown
        config = Config(app=unfazed)
        uvicorn_ls = LifespanOn(config)

        await uvicorn_ls.startup()
        assert hello_life_span.count == 2

        await uvicorn_ls.shutdown()
        assert hello_life_span.count == 3
