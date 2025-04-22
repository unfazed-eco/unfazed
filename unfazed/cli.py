import asyncio
import importlib.util
import os
import typing as t

from unfazed.core import Unfazed


def import_unfazed(current_path: str) -> t.Optional[Unfazed]:
    asgi_location = os.path.join(current_path, "asgi.py")

    if not os.path.exists(asgi_location):
        return None

    # import asgi.py as a module, and get the application object
    # already checked the file exists
    spec = importlib.util.spec_from_file_location("asgi", asgi_location)

    # use assert to skip mypy check
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)

    # use assert to skip mypy check
    assert module is not None
    spec.loader.exec_module(module)

    return module.application


async def _main() -> None:
    current_path = os.getcwd()
    maybeapp = import_unfazed(current_path)
    if maybeapp is None:
        app = Unfazed()
        await app.setup_cli()
        await app.execute_command_from_cli()
    else:
        app = maybeapp
        await app.setup()
        await app.execute_command_from_argv()


def main() -> None:
    asyncio.run(_main())
