from typing import List

from aerich import Command as AerichCommand
from aerich.enums import Color
from click import Option, secho

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "aerich: Show current available heads in migrate location."

    def add_arguments(self) -> List[Option | None]:
        return [
            Option(
                ["--location", "-l"],
                help="Migrate store location.",
                type=str,
                default="./migrations",
                show_default=True,
            ),
        ]

    async def handle(self, **option) -> None:
        location = option.get("location")
        db_conf = self.unfazed.settings.DATABASE.model_dump(exclude_none=True)
        aerich_cmd = AerichCommand(db_conf, location=location)
        await aerich_cmd.init()
        head_list = await aerich_cmd.heads()
        if not head_list:
            return secho("No available heads, try migrate first", fg=Color.green)
        for version in head_list:
            secho(version, fg=Color.green)
