import typing as t
import uuid

from pydantic import BaseModel

SUPPORTED_TYPES = (str, int, float, BaseModel)


def _is_supported_types(annotation: t.Type) -> bool:
    return annotation in SUPPORTED_TYPES


def _generate_random_string() -> str:
    return uuid.uuid4().hex
