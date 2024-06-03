import typing as t

from .orm import OrmModel


class AppCommand(t.Protocol):
    name: str
    import_path: str

    def execute(self) -> None: ...


class AppConfig(t.Protocol):
    name: str
    commands: t.Sequence[AppCommand]
    models: t.Sequence[t.Type[OrmModel]]

    def ready(self) -> None: ...
