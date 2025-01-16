from unittest.mock import patch

from unfazed.command.internal import shell
from unfazed.core import Unfazed


async def test_shell_cmd() -> None:
    unfazed = Unfazed()
    with patch("code.interact") as interact:
        command = shell.Command(unfazed, "shell", "internal")
        await command.handle()
        interact.assert_called_once()
