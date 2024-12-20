import typing as t

import pytest

from unfazed.conf import UnfazedSettings, settings
from unfazed.core import Unfazed
from unfazed.middleware.internal.cors import CORSMiddleware
from unfazed.middleware.internal.gzip import GZipMiddleware
from unfazed.middleware.internal.trustedhost import TrustedHostMiddleware


@pytest.fixture(autouse=True)
def setup_middleware_settings() -> t.Generator:
    settings["UNFAZED_SETTINGS"] = UnfazedSettings()

    yield

    settings.clear()


async def test_failed_setup() -> None:
    app = Unfazed()

    with pytest.raises(ValueError):
        CORSMiddleware(app=app)

    with pytest.raises(ValueError):
        GZipMiddleware(app=app)

    with pytest.raises(ValueError):
        TrustedHostMiddleware(app=app)
