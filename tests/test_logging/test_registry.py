import logging
import typing as t

from unfazed.core import Unfazed
from unfazed.logging import LogCenter

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


EMPTY_LOGGING: t.Dict[str, t.Any] = {}


async def test_registry() -> None:
    unfazed = Unfazed()

    # await unfazed.setup()

    log_center = LogCenter(unfazed, LOGGING)
    log_center.setup()

    # check merged config
    assert log_center.config is not None
    assert log_center.config["version"] == 1
    assert log_center.config["disable_existing_loggers"] is False
    assert "standard" in log_center.config["formatters"]
    assert "_simple" in log_center.config["formatters"]

    assert "default" in log_center.config["handlers"]
    assert "_console" in log_center.config["handlers"]

    assert "unfazed" in log_center.config["loggers"]
    assert "common" in log_center.config["loggers"]

    logger = logging.getLogger("common")
    assert logger.level == logging.WARNING

    # init with empty logging

    log_center2 = LogCenter(unfazed, EMPTY_LOGGING)
    log_center2.setup()

    assert "unfazed" in log_center.config["loggers"]
