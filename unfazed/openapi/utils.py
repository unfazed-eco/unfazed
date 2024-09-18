import typing as t
import uuid

from pydantic import BaseModel

from .spec import Tag

SUPPORTED_TYPES = (str, int, float, BaseModel)


def _build_tag(tag: "Tag" | str | None) -> "Tag" | None:
    if isinstance(tag, str):
        return Tag(name=tag)
    elif tag is None:
        return Tag(name="default")
    else:
        return tag


def _is_supported_types(annotation: t.Type) -> bool:
    return annotation in SUPPORTED_TYPES


def _generate_random_string() -> str:
    return uuid.uuid4().hex
