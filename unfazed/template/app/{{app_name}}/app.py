from unfazed.app import AppConfig as _AppConfig


class AppConfig(_AppConfig):
    def ready(self) -> None:
        pass
