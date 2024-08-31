import typing as t
from functools import wraps
from unittest.mock import PropertyMock, patch

from pytest_mock import MockerFixture

from unfazed.conf import UnfazedSettings


def mock_unfazed_settings(model: UnfazedSettings):
    def outter(coro: t.Coroutine):
        @wraps(coro)
        async def inner(mocker: MockerFixture):
            with patch(
                "unfazed.core.Unfazed.settings",
                new_callable=PropertyMock,
                return_value=model,
            ):
                return await coro(mocker)

        return inner

    return outter
