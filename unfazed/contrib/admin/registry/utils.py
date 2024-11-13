import typing as t

from unfazed.schema import Condtion

TYPE_MAPPING = {
    # python type to field_type
    "str": "CharField",
    "int": "IntegerField",
    "bool": "BooleanField",
    "float": "FloatField",
    "decimal": "FloatField",
    "date": "DateField",
    "datetime": "DatetimeField",
    "time": "TimeField",
    "bytes": "CharField",
    # tortoise type to field_type
    "BigIntField": "IntegerField",
    "BinaryField": "CharField",
    "SmallIntField": "IntegerField",
    "IntField": "IntegerField",
    "CharEnumFieldInstance": "CharField",
    "IntEnumFieldInstance": "IntegerField",
    "UUIDField": "CharField",
    "DecimalField": "FloatField",
    "JSONField": "CharField",
}

SUPPORTED_FIELD_TYPES = [
    "CharField",
    "IntegerField",
    "BooleanField",
    "FloatField",
    "DateField",
    "DatetimeField",
    "TimeField",
    "TextField",
]


def parse_cond(condtion: t.List[Condtion]) -> t.Dict[str, t.Any]:
    ret = {}
    for cond in condtion:
        field = cond.field
        if cond.eq is not None:
            ret[field] = cond.eq
        if cond.lt is not None:
            ret[f"{field}__lt"] = cond.lt
        if cond.gt is not None:
            ret[f"{field}__gt"] = cond.gt
        if cond.lte is not None:
            ret[f"{field}__lte"] = cond.lte
        if cond.gte is not None:
            ret[f"{field}__gte"] = cond.gte
        if cond.icontains is not None:
            ret[f"{field}__icontains"] = cond.icontains
        if cond.contains is not None:
            ret[f"{field}__contains"] = cond.contains
    return ret


def convert_field_type(t: str) -> str:
    if t in SUPPORTED_FIELD_TYPES:
        return t
    return TYPE_MAPPING.get(t, "CharField")
