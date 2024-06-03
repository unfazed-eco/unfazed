from click import Option

from unfazed.command import BaseCommand


class Command(BaseCommand):
    help_text = "Say hello to someone"

    def add_arguments(self):
        return [
            Option(
                ["--name", "-n"],
                type=str,
                help="The name of the person you want to say hello to",
            )
        ]

    async def handle(self, name: str) -> str:
        print(f"Hello {name}!")
        return name
