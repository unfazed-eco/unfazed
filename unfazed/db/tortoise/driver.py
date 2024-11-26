import typing as t
from pathlib import Path

from tortoise import Tortoise

import unfazed
from unfazed.protocol import DataBaseDriver
from unfazed.schema import AppModels, Command, Database

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class Driver(DataBaseDriver):
    def __init__(self, unfazed: "Unfazed", conf: Database) -> None:
        self.conf = conf
        self.unfazed = unfazed

    async def setup(self) -> None:
        # find all models in apps
        if not self.conf.apps:
            self.conf.apps = self.build_apps()

        # init tortoise
        config = self.conf.model_dump(exclude_none=True)
        config.pop("driver")
        await Tortoise.init(config=config)

        # load aerich command
        for c in self.list_aerich_command():
            self.unfazed.command_center.load_command(c)

    async def migrate(self) -> None:
        # must call after setup
        await Tortoise.generate_schemas()

    def build_apps(self) -> t.Dict[str, t.Any]:
        models_list = ["aerich.models"]  # support aerich cmd
        for _, app in self.unfazed.app_center:
            if app.has_models():
                models_list.append(f"{app.name}.models")

        return {"models": AppModels(MODELS=models_list)}

    def list_aerich_command(self) -> t.List[Command]:
        ret = []
        internal_command_dir = Path(unfazed.__path__[0] + "/db/tortoise/commands")
        for command_file in internal_command_dir.glob("*.py"):
            command_name = command_file.stem

            path = f"unfazed.db.tortoise.commands.{command_name}.Command"
            command = Command(path=path, stem=command_name, label="aerich.command")

            ret.append(command)

        return ret
