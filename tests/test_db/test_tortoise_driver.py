from unittest.mock import patch

from unfazed.db.tortoise.driver import Driver


def test_tortoise_1x_enables_global_fallback() -> None:
    with patch(
        "unfazed.db.tortoise.driver.version",
        return_value="1.0.0",
    ):
        assert Driver.get_tortoise_init_kwargs() == {
            "_enable_global_fallback": True,
        }


def test_tortoise_pre_1x_does_not_enable_global_fallback() -> None:
    with patch(
        "unfazed.db.tortoise.driver.version",
        return_value="0.25.4",
    ):
        assert Driver.get_tortoise_init_kwargs() == {}
