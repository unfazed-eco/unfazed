import typing as t
from pathlib import Path

from aerich import Command as AerichCommand
from aerich.enums import Color
from click import Option, secho

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "aerich: Init config file and generate root migrate location."

    def add_arguments(self) -> t.List[Option]:
        return [
            Option(
                ["--safe", "-s"],
                help="Safe mode",
                type=str,
                default=True,
                show_default=True,
            ),
            Option(
                ["--location", "-l"],
                help="Migrate store location.",
                type=str,
                default="./migrations",
                show_default=True,
            ),
        ]

    async def handle(self, **options: t.Any) -> None:
        location = options["location"]
        safe = options["safe"]

        app = "models"

        assert (
            self.unfazed.settings.DATABASE is not None
        ), "No database found in settings"

        db_conf = self.unfazed.settings.DATABASE.model_dump(exclude_none=True)
        aerich_cmd = AerichCommand(db_conf, location=location)

        dirname = Path(location, app)
        try:
            await aerich_cmd.init_db(safe)
            secho(f"Success create app migrate location {dirname}", fg=Color.green)
            secho(f'Success generate schema for app "{app}"', fg=Color.green)
        except FileExistsError:
            return secho(
                f"Inited {app} already, or delete {dirname} and try again.",
                fg=Color.yellow,
            )
