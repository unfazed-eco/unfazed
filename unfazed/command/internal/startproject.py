from pathlib import Path
from typing import List

from click import Option, Parameter
from jinja2 import Template

import unfazed
from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "create a new project"

    def add_arguments(self) -> List[Parameter | None]:
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

    async def handle(self, project_name: str, location: str):
        template_path = Path(unfazed.__path__[0], "template/project")

        location_path = Path(location)
        project_path = location_path / project_name

        if project_path.exists():
            raise FileExistsError(f"Project {project_path} already exists")

        context = {
            "project_name": project_name,
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
