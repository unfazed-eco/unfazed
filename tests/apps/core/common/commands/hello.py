from unfazed.command import BaseCommand


class Command(BaseCommand):
    async def handle(self, **option):
        return "Hello Unfazed!"
