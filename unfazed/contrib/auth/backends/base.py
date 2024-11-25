import typing as t

from unfazed.protocol import BaseAuthBackend as BaseAuthBackendProtocol


class BaseAuthBackend(BaseAuthBackendProtocol):
    def __init__(self, options: t.Dict = {}) -> None:
        self.options = options
