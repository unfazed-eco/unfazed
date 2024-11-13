from unfazed.contrib.admin.registry import parse_cond
from unfazed.schema import Condtion


def test_parse_cond() -> None:
    cond1 = Condtion(
        field="name", eq=1, lt=2, gt=3, lte=4, gte=5, icontains="test", contains="test"
    )

    cond2 = Condtion(
        field="name2",
        eq=1,
    )

    ret = parse_cond([cond1, cond2])
    assert ret == {
        "name": 1,
        "name__lt": 2,
        "name__gt": 3,
        "name__lte": 4,
        "name__gte": 5,
        "name__icontains": "test",
        "name__contains": "test",
        "name2": 1,
    }
