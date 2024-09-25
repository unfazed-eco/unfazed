import typing as t
import uuid

from pydantic import BaseModel

SUPPORTED_TYPES = (str, int, float, BaseModel)


def _is_supported_types(annotation: t.Type) -> bool:
    for supported_type in SUPPORTED_TYPES:
        if issubclass(annotation, supported_type):
            return True
    return False


def _generate_random_string() -> str:
    return uuid.uuid4().hex
