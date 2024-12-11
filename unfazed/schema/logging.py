# refer: https://docs.python.org/3/library/logging.config.html#dictionary-schema-details

import typing as t

from pydantic import BaseModel, Field


class _DefaultFormatter(t.TypedDict):
    format: str | None
    datefmt: str | None
    style: str | None
    validate: bool | None
    defaults: t.Dict[str, t.Any] | None


class _CustomFormatter(BaseModel):
    class_: str = Field(..., alias="()")
    ...  # other formatter-specific attributes


Formatter = t.Annotated[t.Dict, t.Union[_DefaultFormatter, _CustomFormatter]]


class Filter(BaseModel):
    name: str = Field(..., alias="()")


class _Handler(t.TypedDict):
    # class: str  # must have but editor will report error
    level: t.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | None
    formatter: str | None
    filters: t.List[str] | None
    ...  # other handler-specific attributes


Handler = t.Annotated[t.Dict, _Handler]


class RootLogger(BaseModel):
    level: t.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | None = None
    handlers: t.List[str] | None = None


class Logger(RootLogger):
    filters: t.List[str] | None = None
    propagate: bool | None = None


class LogConfig(BaseModel):
    version: int = 1
    formatters: t.Dict[str, Formatter] | None = None
    filters: t.Dict[str, Filter] | None = None
    handlers: t.Dict[str, Handler] | None = None
    loggers: t.Dict[str, Logger] | None = None
    root: RootLogger | None = None
    incremental: bool | None = None
    disable_existing_loggers: bool | None = None
