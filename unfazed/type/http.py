import typing as t

from pydantic import BaseModel

HttpMethod = t.Literal[
    "GET", "POST", "PATCH", "DELETE", "HEAD", "OPTIONS", "PUT", "TRACE"
]
SUPPOTED_REQUEST_TYPE = t.Union[str, int, float, t.List, BaseModel]
