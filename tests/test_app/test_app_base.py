import pytest

from unfazed.app import BaseAppConfig
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app",
}


def test_app_base() -> None:
    unfazed = Unfazed(settings=UnfazedSettings.model_validate(SETTINGS))

    app_common = BaseAppConfig.from_entry("tests.apps.app.common", unfazed)

    assert app_common.name == "tests.apps.app.common"
    assert "tests/apps/app/common" in str(app_common.app_path)
    assert app_common.label == "tests_apps_app_common"
    assert app_common.has_models() is False
    assert app_common.wakeup("admin") is True
    assert app_common.wakeup("notexist") is False
    assert str(app_common) == "tests.apps.app.common"

    # list commands
    app_command = BaseAppConfig.from_entry("tests.apps.cmd.common", unfazed)
    assert len(app_command.list_command()) == 1

    # with init file
    app_withinit = BaseAppConfig.from_entry("tests.apps.app.withinit", unfazed)
    assert "tests/apps/app/withinit" in str(app_withinit.app_path)

    with pytest.raises(ImportError):
        BaseAppConfig.from_entry("tests.apps.app.notexisted", unfazed)

    with pytest.raises(ModuleNotFoundError):
        BaseAppConfig.from_entry("tests.apps.app.noapp", unfazed)

    with pytest.raises(AttributeError):
        BaseAppConfig.from_entry("tests.apps.app.noclass", unfazed)

    with pytest.raises(TypeError):
        BaseAppConfig.from_entry("tests.apps.app.nobase", unfazed)
