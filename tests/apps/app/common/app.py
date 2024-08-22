from unfazed.app import BaseAppConfig


class AppConfig(BaseAppConfig):
    def ready(self):
        return "AppConfig is ready!"
