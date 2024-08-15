import typing as t

from unfazed import utils
from unfazed.core import Unfazed

if t.TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_app_launch(mocker: "MockerFixture"):
    return_value = {
        "UNFAZED_SETTINGS": {
            "DEBUG": True,
            "PROJECT_NAME": "test_app_launch",
            "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
        }
    }
    with mocker.patch.object(utils, "import_setting", return_value=return_value):
        unfazed = Unfazed()
        unfazed.setup()

        assert unfazed.settings.DEBUG is True
        assert unfazed.settings.PROJECT_NAME == "test_app_launch"
