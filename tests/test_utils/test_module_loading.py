import os

import pytest

from unfazed.utils import import_setting, import_string


def test_import_string():
    with pytest.raises(ImportError):
        import_string("")

    module = import_string("unfazed.core.Unfazed")
    assert module.__name__ == "Unfazed"


def test_import_setting():
    with pytest.raises(ValueError):
        import_setting("abc")

    os.environ["UNFAZED_SETTINGS_MODULE"] = "foo.bar"
    with pytest.raises(ImportError):
        import_setting("UNFAZED_SETTINGS_MODULE")

    os.environ["UNFAZED_SETTINGS_MODULE"] = "tests.apps.utils.settings"
    kv = import_setting("UNFAZED_SETTINGS_MODULE")

    assert kv["foo"] == "bar"
