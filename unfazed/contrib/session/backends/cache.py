import time
import uuid

from unfazed.cache import caches
from unfazed.contrib.session.settings import SessionSettings

from .base import SessionBase


class CacheSession(SessionBase):
    PREFIX = "cachesession:"

    def __init__(
        self, session_setting: SessionSettings, session_key: str | None = None
    ) -> None:
        super().__init__(session_setting, session_key)

        _cache_alias = session_setting.cache_alias
        if not _cache_alias:
            raise ValueError("CacheSession Error: need valid cache alias")

        if _cache_alias not in caches:
            raise ValueError(
                f"CacheSession Error: cache alias {_cache_alias} not in caches"
                "Plz check your unfazedsettings `CACHES`"
            )

        self.client = caches[_cache_alias]

    def generate_session_key(self) -> str:
        """
        format:
            {prefix}:{timestamp}:{uuid_hex_str1}:{uuid_hex_str2}
        """
        timestamp = int(time.time() * 1000)
        uuid_hex_str1 = uuid.uuid4().hex
        uuid_hex_str2 = uuid.uuid4().hex

        return f"{self.PREFIX}{timestamp}:{uuid_hex_str1}:{uuid_hex_str2}"

    async def save(self) -> None:
        if not self.session_key:
            self.session_key = self.generate_session_key()

        if not self._session:
            await self.client.delete(self.session_key)

        else:
            await self.client.set(self.session_key, self._session, self.get_max_age())

    async def load(self) -> None:
        if not self.session_key:
            self._session = {}
            return

        ret = await self.client.get(self.session_key)

        # expired or not found
        if not ret:
            self._session = {}

        else:
            self._session = ret
