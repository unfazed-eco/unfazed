from unfazed.app import BaseAppConfig


class AppConfig(BaseAppConfig):
    async def ready(self) -> None:
        print("AppConfig is ready!")
