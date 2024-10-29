import typing as t

import pytest

from unfazed.cache import caches
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture  # pragma: no cover


_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_cache",
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "unfazed_cache1",
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
                "PREFIX": "unfazed_cache1",
            },
        },
        "other": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "unfazed_cache2",
            "OPTIONS": {
                "MAX_ENTRIES": 1000,
                "PREFIX": "unfazed_cache2",
            },
        },
    },
}


async def test_cache_setup(mocker: "MockerFixture") -> None:
    unfazed = Unfazed(settings=UnfazedSettings(**_Settings))

    await unfazed.setup()

    default_cache = caches["default"]
    other_cache = caches["other"]

    assert default_cache.prefix == "unfazed_cache1"
    assert other_cache.prefix == "unfazed_cache2"

    # test non-exist cache
    with pytest.raises(KeyError):
        caches["non-exist"]
