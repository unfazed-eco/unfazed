import typing as t

from unfazed.protocol import Application, DataBaseProtocol


class ConnectionHandler:
    def __init__(self):
        self._connections: dict[str, DataBaseProtocol] = {}

        if t.TYPE_CHECKING:
            self._app = Application()

    def set_app(self, app: Application) -> None:
        self._app = app

    def get_app(self) -> Application:
        return self._app

    def set_connection(self, alias: str, connection: DataBaseProtocol):
        if alias in self._connections:
            raise ValueError(f"Connection {alias} already exists")

        self._connections[alias] = connection

    def get_connection(self, alias: str) -> DataBaseProtocol:
        if alias not in self._connections:
            raise ValueError(f"Connection {alias} does not exist")

        return self._connections[alias]

    def clear(self):
        self._connections.clear()

    def reset_connection(self, alias: str):
        if alias not in self._connections:
            raise ValueError(f"Connection {alias} does not exist")

        self._connections[alias].close()
        self._connections[alias].connect()


connections = ConnectionHandler()
