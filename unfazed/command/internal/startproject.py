from pathlib import Path

import unfazed
from unfazed.command import BaseCommandWithTemplate


class Command(BaseCommandWithTemplate):
    help_text = "Create a new project with template"
    template = Path(unfazed.__path__[0], "template/project")
