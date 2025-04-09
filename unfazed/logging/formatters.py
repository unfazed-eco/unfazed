import typing as t
from logging import LogRecord

import orjson as json

JSON_STR = t.Annotated[str, "A string containing JSON formatted data"]


class UnfazedJsonFormatter:
    """A custom JSON formatter for logging records.

    This formatter converts log records into JSON strings, including only the specified fields.
    It uses orjson for efficient JSON serialization.

    Attributes:
        fields: A list of field names to include in the JSON output.
    """

    def __init__(self, fields: t.List[str]) -> None:
        self.fields = fields

    def format(self, record: LogRecord) -> JSON_STR:
        """Format a log record into a JSON string.

        Args:
            record: The LogRecord to format.

        Returns:
            A JSON string containing the specified fields from the log record.
            Fields that don't exist in the record are silently omitted.

        Example:
            >>> formatter = UnfazedJsonFormatter(["msg", "levelname"])
            >>> record = LogRecord("name", 20, "path", 1, "message", (), None)
            >>> json_str = formatter.format(record)
        """

        body = {
            field: getattr(record, field)
            for field in self.fields
            if hasattr(record, field)
        }
        return json.dumps(body).decode("utf-8")
