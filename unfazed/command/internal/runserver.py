import sys
import typing as t

from click import Option, Parameter
from uvicorn.config import Config
from uvicorn.server import Server
from uvicorn.supervisors import ChangeReload, Multiprocess

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
        server = Server(config)

        sock = config.bind_socket()
        if config.should_reload:
            ChangeReload(config, target=server.run, sockets=[sock]).run()

        elif config.workers > 1:
            Multiprocess(config, target=server.run, sockets=[sock]).run()

        else:
            await server.serve([sock])

        if not server.started and not config.should_reload and config.workers == 1:
            sys.exit(3)
