import pickle
import typing as t

from unfazed.protocol import SerializerBase


class PickleSerializer(SerializerBase):
    def dumps(self, value: t.Any) -> bytes:
        return pickle.dumps(value)

    def loads(self, value: bytes) -> t.Any:
        return pickle.loads(value)
