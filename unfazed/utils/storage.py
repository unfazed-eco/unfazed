import typing as t


class Storage[T]:
    """
    A generic storage class that provides dictionary-like functionality for managing typed data.

    This class implements the standard dictionary interface (__getitem__, __setitem__, etc.)
    while maintaining type safety through Python's type hints.

    Type Parameters:
        T: The type of values to be stored in the storage.

    Example:
        ```python
        from typing import Any

        class CacheBackend:
            def __init__(self, data: Any):
                self.data = data

        class CacheHandler(Storage[CacheBackend]):
            pass

        # Create a cache handler instance
        handler = CacheHandler()

        # Store a cache backend instance
        handler["user_data"] = CacheBackend({"id": 123, "name": "John"})

        # Retrieve the stored data
        cache = handler["user_data"]
        print(cache.data)  # Output: {"id": 123, "name": "John"}
        ```

    Note:
        - All keys must be strings
        - Values must be of type T
        - Raises KeyError if attempting to access a non-existent key
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
