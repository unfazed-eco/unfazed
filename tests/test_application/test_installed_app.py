import typing as t

import pytest

from unfazed import utils
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_installed_apps(mocker: "MockerFixture") -> None:
    return_value = {
        "UNFAZED_SETTINGS": {
            "DEBUG": True,
            "PROJECT_NAME": "test_app_install",
            "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
        }
    }
    with mocker.patch.object(utils, "import_setting", return_value=return_value):
        unfazed = Unfazed()

        # Check if the installed apps are loaded correctly

        # 1. Test if the installed apps have repeated values
        unfazed.settings.INSTALLED_APPS = [
            "tests.test_application.success",
            "tests.test_application.success",
        ]
        with pytest.raises(RuntimeError):
            unfazed.setup()

        # 2. Test if the installed apps are all valid
        unfazed = Unfazed()
        unfazed.settings.INSTALLED_APPS = [
            "tests.test_application.wrongpath",
        ]

        with pytest.raises(ImportError):
            unfazed.setup()

        # 3. dont have app.py under the path
        unfazed = Unfazed()
        unfazed.settings.INSTALLED_APPS = [
            "tests.test_application.noapp",
        ]

        with pytest.raises(ModuleNotFoundError):
            unfazed.setup()

        # 4. dont have AppConfig class
        unfazed = Unfazed()
        unfazed.settings.INSTALLED_APPS = [
            "tests.test_application.noclass",
        ]

        with pytest.raises(AttributeError):
            unfazed.setup()

        # 5. dont inherit from BaseAppConfig
        unfazed = Unfazed()
        unfazed.settings.INSTALLED_APPS = [
            "tests.test_application.nobase",
        ]

        with pytest.raises(TypeError):
            unfazed.setup()

        # 6. didnot impl ready method
        unfazed = Unfazed()
        unfazed.settings.INSTALLED_APPS = [
            "tests.test_application.noready",
        ]

        with pytest.raises(NotImplementedError):
            unfazed.setup()
            noready_app = unfazed.app_center["tests.test_application.noready"]
            noready_app.ready()

        # 7. success case
        unfazed = Unfazed()
        unfazed.settings.INSTALLED_APPS = [
            "tests.test_application.success",
        ]

        unfazed.setup()
        success_app = unfazed.app_center["tests.test_application.success"]

        assert success_app.label == "tests_test_application_success"
        assert success_app.name == "tests.test_application.success"

        # 8. stest double setup
        unfazed = Unfazed()
        unfazed.settings.INSTALLED_APPS = [
            "tests.test_application.success",
        ]

        unfazed.setup()
        with pytest.raises(RuntimeError):
            unfazed.app_center.setup()
        assert unfazed.ready is True
