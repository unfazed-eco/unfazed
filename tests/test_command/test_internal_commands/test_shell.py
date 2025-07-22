from unittest.mock import patch

from unfazed.command.internal import shell
from unfazed.core import Unfazed


async def test_shell_cmd() -> None:
    unfazed = Unfazed()
    with patch("IPython.terminal.ipapp.launch_new_instance") as interact:
        command = shell.Command(unfazed, "shell", "internal")
        command.handle()
        interact.assert_called_once()
