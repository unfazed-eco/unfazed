import typing as t
from typing import List

from aerich import Command as AerichCommand
from aerich import DowngradeError
from aerich.enums import Color
from click import Option, secho

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "aerich: Downgrade to a specific version."

    def add_arguments(self) -> List[Option]:
        return [
            Option(
                ["--location", "-l"],
                help="Migrate store location.",
                type=str,
                default="./migrations",
                show_default=True,
            ),
            Option(
                ["--version", "-v"],
                help="Version to downgrade to.",
                type=int,
                default=-1,
                show_default=True,
            ),
            Option(
                ["--detele", "-d"],
                help="Delete the version.",
                type=str,
                show_default=True,
                default=True,
            ),
        ]

    async def handle(self, **options: t.Any) -> None:
        location = options["location"]
        version = options["version"]
        delete = options["delete"]

        assert (
            self.unfazed.settings.DATABASE is not None
        ), "No database found in settings"
        db_conf = self.unfazed.settings.DATABASE.model_dump(exclude_none=True)
        aerich_cmd = AerichCommand(db_conf, location=location)
        await aerich_cmd.init()
        try:
            files = await aerich_cmd.downgrade(version, delete)
        except DowngradeError as e:
            return secho(str(e), fg=Color.yellow)
        for file in files:
            secho(f"Success downgrade {file}", fg=Color.green)
