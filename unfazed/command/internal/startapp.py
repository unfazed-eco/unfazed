from pathlib import Path

import unfazed
from unfazed.command import BaseCommandWithTemplate


class Command(BaseCommandWithTemplate):
    help_text = "Create a new app"
    template = Path(unfazed.__path__[0], "template/app")
