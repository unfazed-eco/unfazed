from typing import List

from aerich import Command as AerichCommand
from click import Option, secho

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "aerich: Inspect database tables and generate models."

    def add_arguments(self) -> List[Option | None]:
        return [
            Option(
                ["--location", "-l"],
                help="Migrate store location.",
                show_default=True,
                type=str,
                default="./migrations",
            ),
            Option(
                ["--tables", "-t"],
                help="Tables to inspect",
                type=str,
                required=False,
                multiple=True,
            ),
        ]

    async def handle(self, **option) -> None:
        location = option.get("location")
        tables = option.get("tables")
        db_conf = self.unfazed.settings.DATABASE.model_dump(exclude_none=True)
        aerich_cmd = AerichCommand(db_conf, location=location)
        await aerich_cmd.init()
        ret = await aerich_cmd.inspectdb(tables=tables)

        secho(ret)
