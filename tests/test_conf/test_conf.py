import os

from unfazed.conf import settings

_Settings = {
    "UNFAZED_SETTINGS": {
        "DEBUG": True,
        "PROJECT_NAME": "test_conf",
    },
    "APP1_SETTINGS": {"name": "app1"},
}


async def test_setting_proxy() -> None:
    os.environ["UNFAZED_SETTINGS_MODULE"] = "tests.apps.conf.entry.settings"

    settingkv = settings.settingskv

    assert "UNFAZED_SETTINGS" in settingkv
    assert "APP1_SETTINGS" in settingkv

    # unfazed_setting: UnfazedSettings = settings["UNFAZED_SETTINGS"]
    # app1_setting = settings["APP1_SETTINGS"]

    # assert unfazed_setting.PROJECT_NAME == "test_conf"
    # assert app1_setting.name == "app1"

    # with pytest.raises(KeyError):
    #     settings["notfound"]

    # del settings["APP1_SETTINGS"]

    # with pytest.raises(KeyError):
    #     settings["APP1_SETTINGS"]
