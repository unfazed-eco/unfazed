import pytest

from unfazed.app import AppCenter
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app",
}


async def test_app_registry() -> None:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(SETTINGS))

    app_center = AppCenter(
        unfazed, ["tests.apps.app.common", "tests.apps.app.withinit"]
    )

    await app_center.setup()

    assert len(app_center.store) == 2
    assert "tests.apps.app.common" in app_center
    assert "tests.apps.app.withinit" in app_center
    app1 = app_center["tests.apps.app.common"]
    assert app1.name == "tests.apps.app.common"

    key_list = [key for key, _ in app_center]
    assert key_list == ["tests.apps.app.common", "tests.apps.app.withinit"]

    app_center2 = AppCenter(unfazed, ["tests.apps.app.common", "tests.apps.app.common"])

    with pytest.raises(RuntimeError):
        await app_center2.setup()
