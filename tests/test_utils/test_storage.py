import pytest

from unfazed.utils import Storage


class Store(Storage[str]):
    pass


def test_store() -> None:
    store = Store()

    store["foo"] = "bar"
    assert store["foo"] == "bar"
    assert "foo" in store

    with pytest.raises(KeyError):
        store["bar"]

    del store["foo"]
    assert "foo" not in store

    store["foo"] = "bar"
    store["foo2"] = "bar2"

    key_list, value_list = [], []
    for key, val in store:
        key_list.append(key)
        value_list.append(val)

    assert key_list == ["foo", "foo2"]
    assert value_list == ["bar", "bar2"]

    store.clear()

    assert "foo" not in store
