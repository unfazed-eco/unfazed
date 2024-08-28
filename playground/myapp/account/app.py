from unfazed.app import BaseAppConfig


class AppConfig(BaseAppConfig):
    def ready(self):
        print("account app is ready!")
