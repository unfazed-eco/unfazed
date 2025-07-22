import typing as t

from unfazed.command import BaseCommand


class Command(BaseCommand):
    def handle(self, **option: t.Any) -> None:
        print("Hello sync method!")

        return None
