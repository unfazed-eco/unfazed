import typing as t

if t.TYPE_CHECKING:
    from .models import BaseAdmin  # pragma: no cover


class AdminCollector:
    def __init__(self) -> None:
        self._store: t.Dict[str, "BaseAdmin"] = {}

    def set(self, key: str, value: "BaseAdmin", override: bool = False) -> None:
        if key in self._store:
            if not override:
                raise KeyError(f"Key {key} already exists in the store")
        self._store[key] = value

    def __getitem__(self, key: str) -> "BaseAdmin":
        if key not in self._store:
            raise KeyError(f"Key {key} not found in the store")

        return self._store[key]

    def __delitem__(self, key: str) -> None:
        if key not in self._store:
            raise KeyError(f"Key {key} not found in the store")
        del self._store[key]

    def __contains__(self, key: str) -> bool:
        return key in self._store

    def __iter__(self) -> t.Iterator[t.Tuple[str, "BaseAdmin"]]:
        return iter(self._store.items())

    def clear(self) -> None:
        self._store = {}


admin_collector = AdminCollector()
