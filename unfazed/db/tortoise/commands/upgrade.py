import typing as t

from aerich import Command as AerichCommand
from aerich.enums import Color
from click import Option, secho

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "aerich: Upgrade to specified version."

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
                ["--transaction", "-t"],
                help="run in transaction mode.",
                type=bool,
                default=True,
                show_default=True,
            ),
        ]

    async def handle(self, **options: t.Any) -> None:
        location = options["location"]
        transaction = options["transaction"]
        assert (
            self.unfazed.settings.DATABASE is not None
        ), "No database found in settings"
        db_conf = self.unfazed.settings.DATABASE.model_dump(exclude_none=True)
        aerich_cmd = AerichCommand(db_conf, location=location)
        await aerich_cmd.init()
        migrated = await aerich_cmd.upgrade(run_in_transaction=transaction)

        if not migrated:
            secho("No upgrade items found", fg=Color.yellow)
        else:
            for version_file in migrated:
                secho(f"Success upgrade {version_file}", fg=Color.green)
