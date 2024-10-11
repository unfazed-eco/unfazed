import typing as t

from tortoise.fields import TimeField
from tortoise.models import Model


def model_to_dict(instance: Model) -> t.Dict[str, t.Any]:
    """
    Convert a tortoise model instance to a dictionary.

    :param instance: The tortoise model instance to convert.
    """

    ret: t.Dict[str, t.Any] = {}
    for name, field in instance._meta.fields_map.items():
        value = getattr(instance, name)

        if field.__class__ == TimeField:
            value = str(value)
        ret[name] = value

    return ret
