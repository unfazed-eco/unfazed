import typing as t

from pydantic import BaseModel

from unfazed import utils as u
from unfazed.const import UNFAZED_SETTINGS_MODULE
from unfazed.utils import Storage


class SettingsProxy(Storage[t.Type[BaseModel]]):
    unfazed_settings_module = UNFAZED_SETTINGS_MODULE

    def __init__(self) -> None:
        super().__init__()
        self._settingskv = None

    @property
    def settingskv(self) -> None:
        if self._settingskv is None:
            self._settingskv = u.import_setting(self.unfazed_settings_module)
        return self._settingskv

    def guess_client_cls(self, alias: str) -> t.Type[BaseModel]:
        if alias == "UNFAZED_SETTINGS":
            client_str = "unfazed.conf.UnfazedSettings"

        else:
            # extract from settingskv or try to guess from alias
            alias_settings_kv = self.settingskv[alias]
            if "CLIENT_CLASS" in alias_settings_kv:
                client_str = alias_settings_kv["CLIENT_CLASS"]
            else:
                app = alias.lower().replace("_", ".").rsplit(".", 1)[0]
                alias_prefix = alias.rsplit("_", 1)[0]
                client_str = f"{app}.settings.{alias_prefix.capitalize()}Settings"

        return u.import_string(client_str)

    def __getitem__(self, key: str) -> BaseModel:
        if key in self.storage:
            return self.storage[key]

        if key not in self.settingskv:
            raise KeyError(
                f"Key {key} not found in {self.unfazed_settings_module} module"
            )

        client_cls = self.guess_client_cls(key)
        client = client_cls(**self.settingskv[key])
        self.storage[key] = client

        return client

    def clear(self) -> None:
        self._settingskv = None
        return super().clear()


settings = SettingsProxy()
