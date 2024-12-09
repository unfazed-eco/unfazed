import typing as t

from unfazed.command import BaseCommand


class Command(BaseCommand):
    async def handle(self, **option: t.Any) -> None:
        print("Hello Unfazed!")

        return None
