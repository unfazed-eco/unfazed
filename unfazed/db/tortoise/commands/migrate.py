import typing as t

from aerich import Command as AerichCommand
from aerich.enums import Color
from click import Option, secho

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "aerich: Generate migrate changes file."

    def add_arguments(self) -> t.List[Option]:
        return [
            Option(
                ["--location", "-l"],
                help="Migrate store location.",
                type=str,
                default="./migrations",
                show_default=True,
            ),
            Option(
                ["--name", "-n"],
                help="Migration name.",
                type=str,
                default="update",
                show_default=True,
            ),
            Option(
                ["--app", "-a"],
                help="app name.",
                type=str,
                default="models",
                show_default=True,
            ),
        ]

    async def handle(self, **options: t.Any) -> None:
        location = options["location"]
        name = options["name"]
        app = options.get("app", "models")
        assert (
            self.unfazed.settings.DATABASE is not None
        ), "No database found in settings"

        db_conf = self.unfazed.settings.DATABASE.model_dump(exclude_none=True)
        aerich_cmd = AerichCommand(db_conf, app=app, location=location)
        await aerich_cmd.init()

        ret = await aerich_cmd.migrate(name)

        if not ret:
            return secho("No changes detected", fg=Color.yellow)
        secho(f"Success migrate {ret}", fg=Color.green)
