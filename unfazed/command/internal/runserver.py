import sys
import typing as t

from click import Option, Parameter
from uvicorn import server, supervisors
from uvicorn.config import Config

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "Run unfazed server"

    def add_arguments(self) -> t.Sequence[Parameter]:
        return [
            Option(
                ["--host"],
                type=str,
                help="The host to listen on",
                default="127.0.0.1",
                show_default=True,
            ),
            Option(
                ["--port"],
                type=int,
                help="The port to listen on",
                default=9527,
                show_default=True,
            ),
            Option(
                ["--reload"],
                is_flag=True,
                help="Enable auto-reload",
                default=True,
                show_default=True,
            ),
            Option(
                ["--workers"],
                type=int,
                help="Number of worker processes",
                default=1,
                show_default=True,
            ),
            Option(
                ["--log-level"],
                type=str,
                help="Log level",
                default="info",
                show_default=True,
            ),
        ]

    async def handle(
        self,
        host: str,
        port: str,
        reload: bool,
        workers: int,
        log_level: str,
    ) -> None:
        config = Config(
            self.unfazed,
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level=log_level,
        )
        runner = server.Server(config)

        sock = config.bind_socket()
        if config.should_reload:
            supervisors.ChangeReload(config, target=runner.run, sockets=[sock]).run()

        elif config.workers > 1:
            supervisors.Multiprocess(config, target=runner.run, sockets=[sock]).run()

        else:
            await runner.serve([sock])

        if not runner.started and not config.should_reload and config.workers == 1:
            sys.exit(3)
