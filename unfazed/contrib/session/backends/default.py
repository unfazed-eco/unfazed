import base64
import logging

import itsdangerous
import orjson as json
from itsdangerous.exc import BadSignature, BadTimeSignature, SignatureExpired

from unfazed.contrib.session.settings import SessionSettings

from .base import SessionBase

logger = logging.getLogger("unfazed.middleware")


class SigningSession(SessionBase):
    SALT = "unfazed:signingsession"

    def __init__(
        self,
        session_setting: SessionSettings,
        session_key: str | None = None,
    ):
        super().__init__(session_setting, session_key)
        self.signer = itsdangerous.TimestampSigner(
            self.setting.secret_key, salt=self.SALT
        )

    def generate_session_key(self) -> str:
        if not self._session:
            return ""
        data = json.dumps(self._session)
        data_signed = self.signer.sign(data)
        data_encoded = base64.b64encode(data_signed)
        return data_encoded.decode("utf-8")

    async def save(self) -> None:
        self.session_key = self.generate_session_key()

        self.modified = False

    async def load(self) -> None:
        if self.session_key is None:
            self._session = {}
            return

        try:
            _session_key_decoded = base64.b64decode(self.session_key)
        except Exception as e:
            logger.error(f"SigningSession Error: failed decoding {e}")
            self._session = {}
            return

        try:
            _session_bytes = self.signer.unsign(
                _session_key_decoded,
                self.get_max_age(),
            )
        except (BadTimeSignature, SignatureExpired, BadSignature) as e:
            logger.error(f"SigningSession Error: failed unsigning {e}")
            self._session = {}
            return

        self._session = json.loads(_session_bytes.decode("utf-8"))
