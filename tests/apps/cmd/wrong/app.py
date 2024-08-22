from unfazed.app import BaseAppConfig


class AppConfig(BaseAppConfig):
    def ready(self):
        print("AppConfig is ready!")
