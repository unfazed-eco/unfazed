import typing as t

from unfazed.contrib.session.settings import SessionSettings
from unfazed.type import Doc


class SessionBase:
    """
    refer: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie

    """

    def __init__(
        self,
        session_setting: SessionSettings,
        session_key: str | None = None,
    ) -> None:
        self.setting = session_setting
        self.session_key = session_key
        self.modified = False
        self.accessed = False

        self._session: (
            t.Dict[str, t.Annotated[t.Any, Doc(description="can be dumpable")]] | None
        ) = None

    def __contains__(self, key: str) -> bool:
        return key in self._session

    def __getitem__(self, key: str) -> t.Any:
        self.accessed = True
        return self._session[key]

    def __setitem__(self, key: str, value: t.Any) -> None:
        self._session[key] = value
        self.modified = True

    def __delitem__(self, key: str) -> None:
        del self._session[key]
        self.modified = True

    def __bool__(self) -> bool:
        return bool(self._session)

    async def delete(self) -> None:
        self._session = {}
        self.modified = True

    def get_max_age(self) -> int:
        return self.setting.cookie_max_age

    def get_expiry_age(self) -> str | None:
        """
        use max age to control the expiry of the cookie
        """
        if not self._session:
            return "expires=Thu, 01 Jan 1970 00:00:00 GMT; "
        return None

    async def flush(self) -> None:
        await self.delete()

    def generate_session_key(self) -> str:
        """
        Usage:
            create a signed session key
            make sure the session key is unique

        """
        raise NotImplementedError()  # pragma: no cover

    async def save(self) -> None:
        """
        Usage:
            when SessionStore is modified, the method will be called
            itsdangerous.TimestampSinger:
                call generate_session_key to created a signed session key

            Redis:
                call generate_session_key to created a signed session key
                and use the session key as the key to store the session data

        """
        raise NotImplementedError()  # pragma: no cover

    async def load(self) -> None:
        """
        Uasge:
            the method will be called when SessionMiddleware start handling the request
            its goal is to load the session data from `cookie_name`
            then the fllowing middlewares or endpoints and access the session data by

            ```python
            # middleware
            user_info = scope["session"]["{your session key}"]

            # endpoint
            user_info = request.session["{your session key}"]
            ```

        """
        raise NotImplementedError()  # pragma: no cover
