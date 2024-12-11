import json
from logging import LogRecord

from unfazed.logging.formatters import UnfazedJsonFormatter


def test_jsonformatter() -> None:
    f = UnfazedJsonFormatter(["name", "levelname", "msg"])
    record = LogRecord("name", 20, "pathname", 10, "message", tuple(), None)

    ret = json.loads(f.format(record))
    assert ret == {"name": "name", "levelname": "INFO", "msg": "message"}
