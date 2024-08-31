import asyncio

from unfazed.core import Unfazed


async def _main() -> None:
    app = Unfazed()
    await app.setup_cli()
    await app.execute_command_from_cli()


def main() -> None:
    asyncio.run(_main())
