import typing as t
import warnings

from pydantic import BaseModel

from unfazed import utils as u
from unfazed.const import UNFAZED_SETTINGS_MODULE
from unfazed.utils import Storage

T = t.TypeVar("T", bound=BaseModel)


class SettingsProxy(Storage[T]):
    """
    Settings Proxy class for unfazed

    settings will load settings from UNFAZED_SETTINGS_MODULE and cache it.

    Usage:

    ```python

    # your_settings.py

    from pydantic import BaseModel

    class YourSettings(BaseModel):

        YOUR_KEY: str
        YOUR_KEY2: int


    # settings.py

    YOUR_SETTINGS = {
        "CLIENT_CLASS": "your_settings.YourSettings",
        "YOUR_KEY": "value",
        "YOUR_KEY2": 1,

    }

    # your_services.py
    from unfazed.conf import settings

    your_settings: YourSettings = settings["YOUR_SETTINGS"]

    your_settings.YOUR_KEY
    your_settings.YOUR_KEY2

    ```

    """

    unfazed_settings_module = UNFAZED_SETTINGS_MODULE

    def __init__(self) -> None:
        super().__init__()
        self._settingskv: t.Dict[str, t.Any] | None = None
        self._client_cls_map: t.Dict[str, t.Type[BaseModel]] = {}

    @property
    def settingskv(self) -> t.Dict[str, t.Any]:
        if self._settingskv is None:
            self._settingskv = u.import_setting(self.unfazed_settings_module)
        return self._settingskv

    def __getitem__(self, key: str) -> T:
        if key in self.storage:
            return super().__getitem__(key)

        if key in self._client_cls_map:
            ins = t.cast(
                T, self._client_cls_map[key].model_validate(self.settingskv[key])
            )
            self.storage[key] = ins
            return ins

        raise KeyError(f"Setting {key} not found")

    def clear(self) -> None:
        self._settingskv = None
        return super().clear()

    def register_client_cls(self, key: str, cls: t.Type[T]) -> None:
        if key in self._client_cls_map:
            warnings.warn(
                f"Setting {key} already registered, it will be overwritten",
                UserWarning,
                stacklevel=2,
            )
        self._client_cls_map[key] = cls


settings: SettingsProxy = SettingsProxy()
