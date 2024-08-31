from unfazed.command import BaseCommand


class Command(BaseCommand):
    def handle(self):
        print("Command is handled!")
