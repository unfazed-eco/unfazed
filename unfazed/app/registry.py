import typing as t

from unfazed.type import CanBeImported

from .base import BaseAppConfig

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class AppCenter:
    def __init__(
        self, unfazed: "Unfazed", installed_apps: t.List[CanBeImported]
    ) -> None:
        self.unfazed = unfazed
        self.installed_apps = installed_apps
        self._store: t.Dict[str, BaseAppConfig] = {}

    async def setup(self) -> None:
        for app_path in self.installed_apps:
            if app_path in self._store:
                raise RuntimeError(f"App with path {app_path} is already loaded")
            temp_app = self.load_app(app_path)
            await temp_app.ready()
            self._store[temp_app.name] = temp_app

        return None

    def load_app(self, app_path: str) -> BaseAppConfig:
        app_config = BaseAppConfig.from_entry(app_path, self.unfazed)
        return app_config

    def __getitem__(self, key: str) -> BaseAppConfig:
        return self._store[key]

    def __contains__(self, key: str) -> bool:
        return key in self._store

    def __iter__(self) -> t.Iterator[t.Tuple[str, BaseAppConfig]]:
        for key, value in self._store.items():
            yield (key, value)

    @property
    def store(self) -> t.Dict[str, BaseAppConfig]:
        return self._store
