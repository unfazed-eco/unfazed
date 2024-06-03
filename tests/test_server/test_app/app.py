from unfazed.app import AppConfig as _AppConfig


class AppConfig(_AppConfig):
    name = "test_app"

    def ready(self) -> None:
        pass
