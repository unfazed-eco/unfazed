from unittest.mock import patch

from starlette.concurrency import run_in_threadpool

from unfazed.cli import main


async def test_main() -> None:
    with patch("unfazed.command.CliCommandCenter.main") as main_func:
        main_func.return_value = None
        await run_in_threadpool(main)
        assert main_func.call_count == 1
