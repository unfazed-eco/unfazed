import asyncio
import typing as t
from pathlib import Path

from click import Command as ClickCommand
from click import Option, Parameter
from jinja2 import Template
from unfazed import types as tp
from unfazed.protocol import BaseCommandMethod

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed


class BaseCommand(ClickCommand, BaseCommandMethod):
    """
    Usage:
        class MyCommand(BaseCommand):
            help_text = "This is a help text"

        def add_arguments(self) -> List[Parameter]:
            return [
                Option(
                    ["--name", "-n"],
                    type=str,
                    help="The name of the project",
                ),
                Option(
                    ["--directory"],
                    type=str,
                    help="The directory of the project",
                ),
            ]

        async def handle(self, name: str, directory: str) -> None:
            await asyncio.sleep(1)
            print("MyCommand.handle name = {}, dir = {}".format(name, directory))


    """

    help_text = ""

    def __init__(
        self,
        unfazed: "Unfazed",
        name: str,
        app_label: str,
        *,
        context_settings: t.MutableMapping[str, t.Any] | None = None,
        callback: t.Callable[..., t.Any] | None = None,
        params: t.List[Parameter] | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str | None = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
    ) -> None:
        help = help or self.help_text
        params = params or []
        params.extend(self.add_arguments())
        callback = self._callback

        self.unfazed = unfazed
        self.app_label = app_label

        super().__init__(
            name,
            context_settings,
            callback,
            params,
            help,
            epilog,
            short_help,
            options_metavar,
            add_help_option,
            no_args_is_help,
            hidden,
            deprecated,
        )

    def _callback(self, **option: t.Optional[t.Any]) -> None:
        if not asyncio.iscoroutinefunction(self.handle):
            raise TypeError("handle method must be a coroutine")
        asyncio.run(self.handle(**option))


class BaseCommandWithTemplate(BaseCommand):
    def add_arguments(self) -> t.Sequence[Parameter]:
        cwd = Path.cwd()
        return [
            Option(
                ["--name", "-n"],
                type=str,
                help="The name of the project",
            ),
            Option(
                ["--directory", "-d"],
                type=str,
                default=str(cwd),
                help="The directory where the project will be created",
                show_default=True,
            ),
            Option(
                ["--template", "-t"],
                type=str,
                help="The template use to render the project",
                default=self.template,
                show_default=True,
            ),
        ]

    async def handle(
        self,
        name: str,
        directory: tp.PathLike,
        template: tp.PathLike,
    ) -> None:
        render_template = template

        if isinstance(render_template, str):
            render_template = Path(render_template)
        render_dest = Path(directory)

        if not render_dest.exists():
            render_dest.mkdir(parents=True, exist_ok=True)

        context = {
            "project": name,
            "app_name": name,
            "version": self.unfazed.version,
        }

        for root, _, files in render_template.walk():
            for f in files:
                new_root = render_dest / root.relative_to(render_template)
                self.handle_file(root, new_root, f, context)

    def handle_file(
        self,
        root: Path,
        new_root: Path,
        file_path: tp.PathLike,
        context: tp.Context,
    ) -> None:
        new_root_rendered = Path(Template(str(new_root)).render(**context))
        if not new_root_rendered.exists():
            new_root_rendered.mkdir(parents=True, exist_ok=True)

        cur_file = root.joinpath(file_path)
        new_file = new_root_rendered.joinpath(file_path)
        with open(cur_file, "r") as cur_fh, open(new_file, "w") as new_fh:
            rendered_text = Template(cur_fh.read(), autoescape=True).render(**context)
            new_fh.write(rendered_text)
