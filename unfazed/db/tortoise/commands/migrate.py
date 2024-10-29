from typing import List

from aerich import Command as AerichCommand
from aerich.enums import Color
from click import Option, secho

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "aerich: Generate migrate changes file."

    def add_arguments(self) -> List[Option | None]:
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
        ]

    async def handle(self, **option) -> None:
        location = option.get("location")
        name = option.get("name")

        db_conf = self.unfazed.settings.DATABASE.model_dump(exclude_none=True)
        aerich_cmd = AerichCommand(db_conf, location=location)
        await aerich_cmd.init()

        ret = await aerich_cmd.migrate(name)

        if not ret:
            return secho("No changes detected", fg=Color.yellow)
        secho(f"Success migrate {ret}", fg=Color.green)
