from asgiref.local import Local
from pydantic import BaseModel

from unfazed import utils as u
from unfazed.const import UNFAZED_SETTINGS_MODULE


class SettingsProxy:
    unfazed_settings_module = UNFAZED_SETTINGS_MODULE
    thread_critical = False

    def __init__(self) -> None:
        self.storage = Local(self.thread_critical)
        self._settingskv = None

    @property
    def settingskv(self) -> None:
        if self._settingskv is None:
            self._settingskv = u.import_setting(self.unfazed_settings_module)
        return self._settingskv

    def __getitem__(self, alias: str) -> BaseModel:
        try:
            return getattr(self.storage, alias)

        except AttributeError:
            if alias not in self.settingskv:
                raise KeyError(
                    f"Key {alias} not found in {self.unfazed_settings_module} module"
                )

        client_str = self.settingskv[alias]["CLIENT_CLASS"]
        client_cls = u.import_string(client_str)

        client = client_cls(**self.settingskv[alias])

        setattr(self.storage, alias, client)

        return client

    def __setitem__(self, alias: str, value: BaseModel) -> None:
        setattr(self.storage, alias, value)

    def __delitem__(self, alias: str) -> None:
        delattr(self.storage, alias)


settings = SettingsProxy()
