import asyncio
import typing as t

from unfazed.command import BaseCommand


class Command(BaseCommand):
    async def handle(self, **option: t.Any) -> None:
        await asyncio.sleep(0.1)
        print("Hello, World!")
