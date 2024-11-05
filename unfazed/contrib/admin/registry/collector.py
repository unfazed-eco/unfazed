import typing as t

from asgiref.local import Local

from .models import BaseAdminModel


class AdminCollector:
    def __init__(self) -> None:
        self._store: Local = Local()

    def set(self, key: str, value: BaseAdminModel, override: bool = False) -> None:
        if hasattr(self._store, key):
            if not override:
                raise KeyError(f"Key {key} already exists in the store")
        setattr(self._store, key, value)

    def __getitem__(self, key: str) -> BaseAdminModel:
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

    def get_routes(self) -> t.Dict[str, t.Any]:
        ret: t.Dict[str, t.Any] = {}

        for ele in dir(self._store):
            if ele.startswith("__"):
                continue
            obj = getattr(self._store, ele)
            if not isinstance(obj, BaseAdminModel):
                continue

            if obj.model_type in ret:
                ret[obj.model_type].append(obj.to_route())
            else:
                ret[obj.model_type] = [obj.to_route()]

        return ret


admin_collector = AdminCollector()
