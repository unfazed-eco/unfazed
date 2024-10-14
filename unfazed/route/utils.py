import typing as t
import uuid

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

SUPPORTED_TYPES = (str, int, float, BaseModel)


def _is_supported_types(annotation: t.Type) -> bool:
    for supported_type in SUPPORTED_TYPES:
        if issubclass(annotation, supported_type):
            return True
    return False


def _generate_random_string() -> str:
    return uuid.uuid4().hex


def _generate_field_schema(field: FieldInfo) -> t.Dict:
    # trick way to generate field schema
    temp_model: BaseModel = create_model(
        "TempModel", **{"temp": (field.annotation, field)}
    )

    return temp_model.model_json_schema()["properties"]["temp"]


def get_endpoint_name(endpoint: t.Coroutine) -> str:
    return endpoint.__name__
