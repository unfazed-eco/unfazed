from unfazed.app import BaseAppConfig


class AppConfig(BaseAppConfig):
    async def ready(self) -> None:
        pass
