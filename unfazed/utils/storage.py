import typing as t


class Storage[T]:
    """
    Generic storage class.
    Use to manage data in a dictionary-like object.

    Example:
    ```python

    class CacheHandler(Storage[CacheBackend]):
        pass

    handler = CacheHandler()
    handler["key"] = CacheBackend()

    ```
    """

    def __init__(self) -> None:
        self.storage: t.Dict[str, T] = {}

    def __getitem__(self, key: str) -> T:
        try:
            return self.storage[key]
        except KeyError:
            raise KeyError(f"{self.__class__.__name__} Error: {key} not found")

    def __setitem__(self, key: str, value: T) -> None:
        self.storage[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.storage

    def __delitem__(self, key: str) -> None:
        del self.storage[key]

    def __iter__(self) -> t.Iterator[t.Tuple[str, T]]:
        for key, value in self.storage.items():
            yield key, value

    def clear(self) -> None:
        self.storage.clear()
