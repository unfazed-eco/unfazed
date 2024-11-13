import pytest

from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed

SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_install",
    "ROOT_URLCONF": "tests.apps.app.routes",
}


async def test_installed_apps(capsys) -> None:
    unfazed = Unfazed(settings=UnfazedSettings(**SETTINGS))

    # Check if the installed apps are loaded correctly

    # 1. Test if the installed apps have repeated values
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.common",
        "tests.apps.app.common",
    ]
    with pytest.raises(RuntimeError):
        await unfazed.setup()

    # 2. Test if the installed apps are all valid
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.notexist",
    ]

    with pytest.raises(ImportError):
        await unfazed.setup()

    # 3. dont have app.py under the path
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.noapp",
    ]

    with pytest.raises(ModuleNotFoundError):
        await unfazed.setup()

    # 4. dont have AppConfig class
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.noclass",
    ]

    with pytest.raises(AttributeError):
        await unfazed.setup()

    # 5. dont inherit from BaseAppConfig
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.nobase",
    ]

    with pytest.raises(TypeError):
        await unfazed.setup()

    # 6. didnot impl ready method
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.noready",
    ]

    with pytest.raises(NotImplementedError):
        await unfazed.setup()
        noready_app = unfazed.app_center["tests.apps.app.noready"]
        noready_app.ready()

    # 7. success case
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.common",
    ]

    await unfazed.setup()
    success_app = unfazed.app_center["tests.apps.app.common"]

    assert "tests.apps.app.common" in unfazed.app_center.store

    assert success_app.label == "tests_apps_app_common"
    assert success_app.name == "tests.apps.app.common"
    assert str(success_app) == "tests.apps.app.common"

    ret = success_app.wakeup("admin")
    assert ret is True
    screen = capsys.readouterr()
    assert screen.out == "hello, unfazed\n"

    ret = success_app.wakeup("notexist")
    assert ret is False

    # 8. test double setup
    unfazed = Unfazed()
    unfazed.settings.INSTALLED_APPS = [
        "tests.apps.app.common",
    ]

    await unfazed.setup()
    with pytest.raises(RuntimeError):
        await unfazed.app_center.setup()
    assert unfazed.ready is True
