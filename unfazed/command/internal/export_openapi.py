import typing as t
from pathlib import Path

from click import Option

from unfazed.command import BaseCommand
from unfazed.openapi import OpenApi

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


class Command(BaseCommand):
    help_text = """
    Export the OpenAPI schema to a file

    Usage:
    >>> unfazed-cli export-openapi --location ./openapi.yaml
    """

    def add_arguments(self) -> t.List[Option]:
        return [
            Option(
                ["--location", "-l"],
                type=str,
                help="location of the file",
                default=str(Path.cwd()),
            ),
        ]

    @t.override
    def handle(self, **options: t.Any) -> None:
        assert yaml is not None, "yaml is not installed"
        assert OpenApi.schema is not None, "OpenAPI schema is not found"

        location = Path(options["location"])

        with open(location / "openapi.yaml", "w") as f:
            yaml.dump(OpenApi.schema, f, sort_keys=False)

        print(f"OpenAPI schema exported to {location / 'openapi.yaml'}")
