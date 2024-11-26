import typing as t

from unfazed.core import Unfazed
from unfazed.logging import LogCenter

if t.TYPE_CHECKING:
    pass


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "common": {  # root logger
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}


def test_registry() -> None:
    unfazed = Unfazed()

    log_center = LogCenter(unfazed, LOGGING)

    # check merged config

    assert log_center.config is not None
    assert log_center.config["version"] == 1
    assert log_center.config["disable_existing_loggers"] is False
    assert "standard" in log_center.config["formatters"]
    assert "_simple" in log_center.config["formatters"]

    assert "default" in log_center.config["handlers"]
    assert "_console" in log_center.config["handlers"]

    assert "unfazed.request" in log_center.config["loggers"]
    assert "unfazed.server" in log_center.config["loggers"]
    assert "unfazed.middleware" in log_center.config["loggers"]
    assert "common" in log_center.config["loggers"]
