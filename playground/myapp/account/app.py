from unfazed.app import BaseAppConfig


class AppConfig(BaseAppConfig):
    async def ready(self):
        print("account app is ready!")
