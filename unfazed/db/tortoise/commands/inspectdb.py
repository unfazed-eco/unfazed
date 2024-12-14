import typing as t

from aerich import Command as AerichCommand
from click import Option, secho

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "aerich: Inspect database tables and generate models."

    def add_arguments(self) -> t.List[Option]:
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

    async def handle(self, **options: t.Any) -> None:
        location = options["location"]
        tables = options["tables"]
        assert (
            self.unfazed.settings.DATABASE is not None
        ), "No database found in settings"
        db_conf = self.unfazed.settings.DATABASE.model_dump(exclude_none=True)
        aerich_cmd = AerichCommand(db_conf, location=location)
        await aerich_cmd.init()
        ret = await aerich_cmd.inspectdb(tables=tables)

        secho(ret)
