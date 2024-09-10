import typing as t
from logging import LogRecord

import orjson as json

JSON_STR = t.Annotated[str, "json_str"]


class UnfazedJsonFormatter:
    def __init__(self, fields: t.List[str]) -> None:
        self.fields = fields

    def format(self, record: LogRecord) -> JSON_STR:
        body = {
            field: getattr(record, field)
            for field in self.fields
            if hasattr(record, field)
        }
        return json.dumps(body).decode("utf-8")
