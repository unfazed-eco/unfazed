class Storage[T]:
    def __init__(self) -> None:
        self.storage = {}

    def __getitem__(self, key: str) -> T:
        try:
            return self.storage[key]
        except KeyError:
            raise KeyError(f"Unfazed Error: {key} not found")

    def __setitem__(self, key: str, value: T) -> None:
        self.storage[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.storage

    def __delitem__(self, key: str) -> None:
        del self.storage[key]

    def clear(self) -> None:
        self.storage.clear()
