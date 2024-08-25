from unfazed.command import BaseCommand


class Command(BaseCommand):
    async def handle(self, **options):
        print("Hello, World!")
