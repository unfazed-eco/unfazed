import typing as t

from unfazed.command import BaseCommand


class Command(BaseCommand):
    async def handle(self, **options: t.Any) -> None:
        print("Command is handled!")
