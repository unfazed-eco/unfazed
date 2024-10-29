from unfazed.app import BaseAppConfig


class AppConfig(BaseAppConfig):
    async def ready(self):
        print("AppConfig is ready!")
