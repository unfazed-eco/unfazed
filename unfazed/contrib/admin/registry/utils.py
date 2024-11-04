import typing as t

from unfazed.schema import Condtion


def parse_cond(condtion: t.List[Condtion]) -> t.Dict[str, t.Any]:
    ret = {}
    for cond in condtion:
        field = cond.field
        if cond.eq is not None:
            ret[field] = cond.eq
        elif cond.lt is not None:
            ret[f"{field}__lt"] = cond.lt
        elif cond.gt is not None:
            ret[f"{field}__gt"] = cond.gt
        elif cond.lte is not None:
            ret[f"{field}__lte"] = cond.lte
        elif cond.gte is not None:
            ret[f"{field}__gte"] = cond.gte
        elif cond.icontains is not None:
            ret[f"{field}__icontains"] = cond.icontains
        elif cond.contains is not None:
            ret[f"{field}__icontains"] = cond.contains
    return ret
