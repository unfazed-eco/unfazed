import pytest
from pydantic import BaseModel

from unfazed.contrib.admin.registry import BaseAdmin, admin_collector


# for mypy check
class HypoSerializer(BaseModel):
    pass


class Admin1(BaseAdmin):
    serializer = HypoSerializer


class Admin2(BaseAdmin):
    serializer = HypoSerializer


def test_admin_collector() -> None:
    admin1 = Admin1()
    admin_collector.set("admin1", admin1)
    assert admin_collector["admin1"] == admin1

    assert "admin1" in admin_collector

    with pytest.raises(KeyError):
        admin_collector.set("admin1", admin1)

    admin2 = Admin2()
    admin_collector.set("admin1", admin2, override=True)
    assert admin_collector["admin1"] == admin2

    with pytest.raises(KeyError):
        admin_collector["notfound"]

    del admin_collector["admin1"]

    assert "admin1" not in admin_collector

    with pytest.raises(KeyError):
        del admin_collector["notfound"]

    admin_collector.set("admin2", admin2)
    admin_collector.clear()

    assert "admin2" not in admin_collector
