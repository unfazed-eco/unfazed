import typing as t

from unfazed.app import AppCenter
from unfazed.protocol import DataBaseDriver
from unfazed.schema import AppModels, Database
from unfazed.utils import import_string


class ModelCenter:
    def __init__(self, conf: t.Dict, app_center: AppCenter) -> None:
        self.conf = Database(**conf)
        self.app_center = app_center

    def setup(self):
        driver_cls = import_string(self.conf.driver)
        if not self.conf.apps:
            self.conf.apps = self.build_apps()
        driver: DataBaseDriver = driver_cls(self.conf)
        driver.setup()

    def build_apps(self) -> t.Dict[str, t.Any]:
        ret = {}
        for alias, app in self.app_center:
            model_list = app.list_model()

            ret[alias] = AppModels(models=model_list)

        return ret
