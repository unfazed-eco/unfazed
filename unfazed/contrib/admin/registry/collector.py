import typing as t

from asgiref.local import Local


class AdminCollector:
    def __init__(self) -> None:
        self._store: Local = Local()

    def set(self, key: str, value: t.Any, override: bool = False) -> None:
        if hasattr(self._store, key):
            if not override:
                raise KeyError(f"Key {key} already exists in the store")
        setattr(self._store, key, value)

    def __getitem__(self, key: str) -> t.Any:
        if not hasattr(self._store, key):
            raise KeyError(f"Key {key} not found in the store")

        return getattr(self._store, key)

    def __delitem__(self, key: str) -> None:
        if not hasattr(self._store, key):
            raise KeyError(f"Key {key} not found in the store")
        delattr(self._store, key)

    def __contains__(self, key: str) -> bool:
        return hasattr(self._store, key)

    def clear(self) -> None:
        self._store = Local()


admin_collector = AdminCollector()
