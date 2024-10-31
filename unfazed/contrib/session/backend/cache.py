import time
import uuid

from .base import SessionBase


class CacheSession(SessionBase):
    PREFIX = "cachesession:"

    def generate_session_id(self) -> str:
        """
        format:
            {prefix}:{timestamp}:{uuid_hex_str1}:{uuid_hex_str2}
        """
        timestamp = int(time.time() * 1000)
        uuid_hex_str1 = uuid.uuid4().hex
        uuid_hex_str2 = uuid.uuid4().hex

        return f"{self.PREFIX}{timestamp}:{uuid_hex_str1}:{uuid_hex_str2}"
