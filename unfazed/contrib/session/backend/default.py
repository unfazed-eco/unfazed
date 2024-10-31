import itsdangerous
import orjson as json

from .base import SessionBase


class SigningSession(SessionBase):
    PREFIX = "signingsession:"

    def __init__(self, session_setting, session_key=None):
        super().__init__(session_setting, session_key)

        salt = f"{self.PREFIX}:{self.setting.cookie_name}"
        self.signer = itsdangerous.TimestampSigner(self.setting.secret_key, salt=salt)

    def generate_session_id(self) -> str:
        data = json.dumps(self._session)
        return self.signer.sign(data)

    async def save(self) -> None:
        self.session_key = self.generate_session_id()

    async def delete(self) -> None:
        self._session = {}

    async def load(self) -> None:
        _session_str = self.signer.unsign(
            self.session_key, self.get_max_age(), return_timestamp=True
        ).decode("utf-8")
        _session = json.loads(_session_str)

    def get_max_age(self) -> int:
        return self.setting.cookie_max_age
