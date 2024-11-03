import pickle
import typing as t

from unfazed.protocol import SerializerBase


class PickleSerializer(SerializerBase):
    PROTOCOL = pickle.HIGHEST_PROTOCOL

    def dumps(self, value: t.Any) -> bytes:
        return pickle.dumps(value, protocol=self.PROTOCOL)

    def loads(self, value: bytes) -> t.Any:
        return pickle.loads(value)
