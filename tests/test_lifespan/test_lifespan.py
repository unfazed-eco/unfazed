from unittest.mock import PropertyMock, patch

import pytest

from unfazed.conf import UnfazedSettings
from unfazed.core.application import Unfazed
from unfazed.lifespan import lifespan_handler
from unfazed.protocol import BaseLifeSpan
from unfazed.test import Requestfactory


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
    "LIFESPAN": [
        "tests.test_lifespan.test_lifespan.HelloLifeSpan",
    ],
}


async def test_registry() -> None:
    unfazed = Unfazed(settings=UnfazedSettings(**SETTINGS))
    lifespan_handler.clear()
    await unfazed.setup()

    hello_lifespan = lifespan_handler.get(
        "tests.test_lifespan.test_lifespan.HelloLifeSpan"
    )

    with Requestfactory(unfazed):
        assert hello_lifespan.count == 2

    assert hello_lifespan.count == 3


SETTINGS2 = {
    "DEBUG": True,
    "PROJECT_NAME": "test_lifespan",
    "LIFESPAN": [
        "tests.test_lifespan.test_lifespan.HelloLifeSpan",
        "tests.test_lifespan.test_lifespan.HelloLifeSpan",
    ],
}


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
    "LIFESPAN": [
        "tests.test_lifespan.test_lifespan.HelloLifeSpan2",
    ],
}


async def test_empty_state() -> None:
    unfazed = Unfazed(settings=UnfazedSettings(**SETTINGS3))
    lifespan_handler.clear()
    await unfazed.setup()
    hello_lifespan = lifespan_handler.get(
        "tests.test_lifespan.test_lifespan.HelloLifeSpan2"
    )

    with Requestfactory(unfazed):
        assert hello_lifespan.count == 2

    assert hello_lifespan.count == 3
