import os

from unfazed.core import Unfazed


def test_models_center():
    os.environ["UNFAZED_SETTINGS_MODULE"] = "unfazedproject.settings"

    unfazed = Unfazed()

    unfazed.setup_models()

    models = unfazed.models_center.models
    assert len(models) == 1
