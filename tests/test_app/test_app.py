import typing as t

import pytest

from tests.decorators import mock_unfazed_settings
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_install",
    "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
    "ROOT_URLCONF": "tests.apps.app.routes",
}


@mock_unfazed_settings(UnfazedSettings(**SETTINGS))
def test_installed_apps(mocker: "MockerFixture") -> None:
    unfazed = Unfazed()

    # Check if the installed apps are loaded correctly

    # 1. Test if the installed apps have repeated values
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.common",
        "tests.apps.app.common",
    ]
    with pytest.raises(RuntimeError):
        unfazed.setup()

    # 2. Test if the installed apps are all valid
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.notexist",
    ]

    with pytest.raises(ImportError):
        unfazed.setup()

    # 3. dont have app.py under the path
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.noapp",
    ]

    with pytest.raises(ModuleNotFoundError):
        unfazed.setup()

    # 4. dont have AppConfig class
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.noclass",
    ]

    with pytest.raises(AttributeError):
        unfazed.setup()

    # 5. dont inherit from BaseAppConfig
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.nobase",
    ]

    with pytest.raises(TypeError):
        unfazed.setup()

    # 6. didnot impl ready method
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.noready",
    ]

    with pytest.raises(NotImplementedError):
        unfazed.setup()
        noready_app = unfazed.app_center["tests.apps.app.noready"]
        noready_app.ready()

    # 7. success case
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.common",
    ]

    unfazed.setup()
    success_app = unfazed.app_center["tests.apps.app.common"]

    assert success_app.label == "tests_apps_app_common"
    assert success_app.name == "tests.apps.app.common"

    # 8. test double setup
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.common",
    ]

    unfazed.setup()
    with pytest.raises(RuntimeError):
        unfazed.app_center.setup()
    assert unfazed.ready is True
