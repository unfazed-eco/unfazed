import typing as t


class Settings(t.Protocol):
    def from_key(self, key: str) -> t.Self: ...
