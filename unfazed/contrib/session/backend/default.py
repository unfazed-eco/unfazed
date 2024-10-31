import itsdangerous
import orjson as json
from itsdangerous.exc import BadSignature, BadTimeSignature, SignatureExpired

from unfazed.contrib.session.settings import SessionSettings

from .base import SessionBase


class SigningSession(SessionBase):
    PREFIX = "signingsession:"

    def __init__(
        self,
        session_setting: SessionSettings,
        session_key: str | None = None,
    ):
        super().__init__(session_setting, session_key)

        salt = f"{self.PREFIX}:{self.setting.cookie_domain}"
        self.signer = itsdangerous.TimestampSigner(self.setting.secret_key, salt=salt)

    @property
    def header_value(self) -> str:
        if self._session:
            data = json.dumps(self._session).decode("utf-8")
        else:
            data = "null"

        security_flags = "httponly; samesite=" + self.setting.cookie_samesite
        if self.setting.cookie_httponly:  # Secure flag can be used with HTTPS only
            security_flags += "; secure"
        if self.setting.cookie_domain is not None:
            security_flags += f"; domain={self.setting.cookie_domain}"
        header_value = (
            "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(
                session_cookie=self.setting.cookie_name,
                data=data,
                path=self.setting.cookie_path,
                max_age=f"Max-Age={self.get_max_age()}; " if self.get_max_age() else "",
                security_flags=self.security_flags,
            )
        )

        return header_value

    def generate_session_id(self) -> str:
        data = json.dumps(self._session)
        return self.signer.sign(data)

    async def save(self) -> None:
        self.session_key = self.generate_session_id()

    async def delete(self) -> None:
        self._session = {}

    async def load(self) -> None:
        if self.session_key is None:
            self._session = {}
            return

        try:
            _session_bytes = self.signer.unsign(
                self.session_key,
                self.get_max_age(),
            )
        except (BadTimeSignature, SignatureExpired, BadSignature):
            self._session = {}
            return

        self._session = json.loads(_session_bytes.decode("utf-8"))

    def get_max_age(self) -> int:
        return self.setting.cookie_max_age
