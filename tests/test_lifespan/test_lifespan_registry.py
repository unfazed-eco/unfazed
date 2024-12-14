import typing as t

import pytest

from unfazed.conf import UnfazedSettings
from unfazed.core.application import Unfazed
from unfazed.lifespan import BaseLifeSpan, lifespan_handler
from unfazed.test import Requestfactory


class HelloLifeSpan(BaseLifeSpan):
    def __init__(self, unfazed: Unfazed) -> None:
        super().__init__(unfazed)
        self.count = 1

    async def on_startup(self) -> None:
        self.count += 1

    @property
    def state(self) -> t.Dict:
        return {"foo": "bar"}


class HelloLifeSpan2(BaseLifeSpan):
    def __init__(self, unfazed: Unfazed) -> None:
        super().__init__(unfazed)
        self.count = 1

    async def on_shutdown(self) -> None:
        self.count += 1


SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_serializer",
    "LIFESPAN": [
        "tests.test_lifespan.test_lifespan_registry.HelloLifeSpan",
    ],
}


async def test_registry() -> None:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(SETTINGS))
    lifespan_handler.clear()
    await unfazed.setup()

    hello_lifespan: HelloLifeSpan = t.cast(
        HelloLifeSpan,
        lifespan_handler.get(
            "tests.test_lifespan.test_lifespan_registry.HelloLifeSpan"
        ),
    )

    async with Requestfactory(unfazed):
        assert hello_lifespan.count == 2


SETTINGS2 = {
    "DEBUG": True,
    "PROJECT_NAME": "test_lifespan",
    "LIFESPAN": [
        "tests.test_lifespan.test_lifespan_registry.HelloLifeSpan",
        "tests.test_lifespan.test_lifespan_registry.HelloLifeSpan",
    ],
}


async def test_failed() -> None:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(SETTINGS2))

    with pytest.raises(ValueError):
        await unfazed.setup()


SETTINGS3 = {
    "DEBUG": True,
    "PROJECT_NAME": "test_lifespan",
    "LIFESPAN": [
        "tests.test_lifespan.test_lifespan_registry.HelloLifeSpan2",
    ],
}


async def test_empty_state() -> None:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(SETTINGS3))
    lifespan_handler.clear()
    await unfazed.setup()
    hello_lifespan: HelloLifeSpan2 = t.cast(
        HelloLifeSpan2,
        lifespan_handler.get(
            "tests.test_lifespan.test_lifespan_registry.HelloLifeSpan2"
        ),
    )

    async with Requestfactory(unfazed):
        assert hello_lifespan.count == 1

    assert hello_lifespan.count == 2
