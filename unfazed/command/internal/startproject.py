import typing as t
import uuid
from pathlib import Path

from click import Option
from jinja2 import Template

import unfazed
from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = """

    Create a new project from cli

    Usage:
    >>> unfazed-cli startproject -n myproject

    """

    @t.override
    def add_arguments(self) -> t.List[Option]:
        return [
            Option(
                ["--project_name", "-n"],
                help="name of the project",
                type=str,
            ),
            Option(
                ["--location", "-l"],
                help="location of the project",
                type=str,
                default=str(Path.cwd()),
                show_default=True,
            ),
        ]

    async def handle(self, **options: t.Any) -> None:
        project_name = options["project_name"]
        location = options["location"]
        template_path = Path(unfazed.__path__[0], "template/project")

        location_path = Path(location)
        project_path = location_path / project_name

        if project_path.exists():
            raise FileExistsError(f"Project {project_path} already exists")

        context = {
            "project_name": project_name,
            "secret": uuid.uuid4().hex + uuid.uuid4().hex,
        }

        for root, _, files in template_path.walk():
            for f in files:
                new_root = location_path / root.relative_to(template_path)
                self.handle_file(root, new_root, f, context)

    def handle_file(
        self,
        root: Path,
        new_root: Path,
        file_path: str,
        context: dict,
    ) -> None:
        new_root_rendered = Path(Template(str(new_root)).render(**context))
        if not new_root_rendered.exists():
            new_root_rendered.mkdir(parents=True, exist_ok=True)

        cur_file = root.joinpath(file_path)
        if file_path.endswith(".py.tpl"):
            file_path = file_path[:-4]
        new_file = new_root_rendered.joinpath(file_path)
        with open(cur_file, "r") as cur_fh, open(new_file, "w") as new_fh:
            rendered_text = Template(cur_fh.read(), autoescape=True).render(**context)
            new_fh.write(rendered_text)
