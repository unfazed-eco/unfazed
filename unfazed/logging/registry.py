import copy
import typing as t
from logging.config import dictConfig

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


DEFAULT_LOGGING_CONFIG = {
    "formatters": {
        "_simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "_console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "_simple",
        }
    },
    "loggers": {
        "unfazed": {
            "level": "DEBUG",
            "handlers": ["_console"],
        },
        "unvicorn": {
            "level": "INFO",
            "handlers": ["_console"],
        },
        "tortoise": {
            "level": "INFO",
            "handlers": ["_console"],
        },
    },
    "filters": {},
    # "root": {"level": "DEBUG", "handlers": ["_console"]},
    "version": 1,
}


class LogCenter:
    def __init__(self, unfazed: "Unfazed", dictconfig: t.Dict) -> None:
        self.unfazed = unfazed
        self.raw_dictconfig = dictconfig
        self.config = self.merge_default(dictconfig)

    def setup(self) -> None:
        dictConfig(self.config)

    def merge_default(self, dictconfig: t.Dict) -> t.Dict:
        ret = copy.deepcopy(DEFAULT_LOGGING_CONFIG)

        if not dictconfig:
            return ret

        for key in dictconfig:
            if key not in ret:
                ret[key] = dictconfig[key]

            elif key in ["handlers", "formatters", "filters", "loggers"]:
                # ret[key].update(dictconfig[key])
                target = t.cast(t.Dict, ret[key])
                target.update(dictconfig[key])

            else:
                continue

        return ret
