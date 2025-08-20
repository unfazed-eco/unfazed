import typing as t

if t.TYPE_CHECKING:
    from .models import (  # pragma: no cover
        BaseAdmin,
        CustomAdmin,
        ModelAdmin,
        ModelInlineAdmin,
    )

from unfazed.utils import Storage

T = t.TypeVar(
    "T", bound=t.Union["BaseAdmin", "ModelAdmin", "ModelInlineAdmin", "CustomAdmin"]
)


class AdminCollector(Storage[T]):
    def set(self, key: str, value: T, override: bool = False) -> None:
        if key in self.storage:
            if not override:
                raise KeyError(f"Key {key} already exists in the store")
        self.storage[key] = value

    def __iter__(self) -> t.Iterator[t.Tuple[str, T]]:
        for key, value in self.storage.items():
            yield key, value


admin_collector: AdminCollector = AdminCollector()
