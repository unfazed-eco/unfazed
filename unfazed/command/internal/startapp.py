from pathlib import Path
from typing import List

from click import Choice, Option
from jinja2 import Template

import unfazed
from unfazed.command import BaseCommand


class TemplateType:
    SIMPLE = "simple"
    COMPLEX = "complex"


class Command(BaseCommand):
    help_text = "create a new app under the project"

    def add_arguments(self) -> List[Option | None]:
        cwd = Path.cwd()
        return [
            Option(
                ["--app_name", "-n"],
                help="name of the app",
                type=str,
            ),
            Option(
                ["--location", "-l"],
                help="location of the app",
                type=str,
                default=str(cwd),
                show_default=True,
            ),
            Option(
                ["--template", "-t"],
                help="template path of the app",
                type=Choice([TemplateType.SIMPLE, TemplateType.COMPLEX]),
                default=TemplateType.SIMPLE,
                show_default=True,
                show_choices=True,
            ),
        ]

    async def handle(self, app_name: str, location: str, template: str):
        if template == TemplateType.SIMPLE:
            template_path = Path(unfazed.__path__[0], "template/app/simple")
        elif template == TemplateType.COMPLEX:
            template_path = Path(unfazed.__path__[0], "template/app/complex")
        else:
            raise ValueError(f"Unknown template type: {template}")

        location_path = Path(location)
        app_path = location_path / app_name

        if app_path.exists():
            raise FileExistsError(f"App {app_name} already exists")

        context = {
            "app_name": app_name,
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
