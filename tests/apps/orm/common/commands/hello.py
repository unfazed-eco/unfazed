import asyncio

from unfazed.command import BaseCommand


class Command(BaseCommand):
    async def handle(self, **options):
        await asyncio.sleep(0.1)
        print("Hello, World!")
