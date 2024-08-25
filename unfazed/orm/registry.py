import typing as t

from unfazed.app import AppCenter
from unfazed.protocol import DataBaseDriver
from unfazed.schema import AppModels, Database
from unfazed.utils import import_string


class ModelCenter:
    def __init__(self, conf: Database, app_center: AppCenter) -> None:
        self.app_center = app_center
        self.conf = conf

    async def setup(self):
        if not self.conf:
            return
        driver_cls = import_string(self.conf.driver)
        if not self.conf.apps:
            self.conf.apps = self.build_apps()
        driver: DataBaseDriver = driver_cls(self.conf.model_dump(exclude_none=True))
        await driver.setup()

    def build_apps(self) -> t.Dict[str, t.Any]:
        models_list = ["aerich.models"]  # support aerich cmd
        for _, app in self.app_center:
            if app.has_models():
                models_list.append(f"{app.name}.models")

        return {"models": AppModels(MODELS=models_list)}
