import typing as t

from unfazed.contrib.session.settings import SessionSettings
from unfazed.type import Doc


class SessionBase:
    def __init__(
        self,
        session_setting: SessionSettings,
        session_key: str | None = None,
    ) -> None:
        self.setting = session_setting
        self.session_key = session_key
        self.modified = False

        self._session: (
            t.Dict[str, t.Annotated[t.Any, Doc(description="can be dumpable")]] | None
        ) = None

    def __contains__(self, key: str) -> bool:
        return key in self._session

    def __getitem__(self, key: str) -> t.Any:
        return self._session[key]

    def __setitem__(self, key: str, value: t.Any) -> None:
        self._session[key] = value
        self.modified = True

    def __delitem__(self, key: str) -> None:
        del self._session[key]
        self.modified = True

    def __bool__(self) -> bool:
        return bool(self._session)

    @property
    def header_value(self) -> str:
        raise NotImplementedError()

    def generate_session_id(self) -> str:
        raise NotImplementedError()

    async def save(self) -> None:
        raise NotImplementedError()

    async def delete(self) -> None:
        raise NotImplementedError()

    async def load(self) -> None:
        raise NotImplementedError()

    def get_max_age(self) -> int:
        raise NotImplementedError()

    async def set_expiry(self, value: int) -> None:
        raise NotImplementedError()

    def get_expiry_age(self) -> int:
        raise NotImplementedError()

    async def flush(self) -> None:
        raise NotImplementedError()
