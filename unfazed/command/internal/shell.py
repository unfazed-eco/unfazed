import code
import typing as t

from unfazed.command import BaseCommand


class Command(BaseCommand):
    """
    Currently, unfazed only support default python shell

    Ipython not supported yet

    """

    help_text = """

    Run the unfazed Shell

    Usage:

    >>> python manage.py shell
    """

    async def handle(self, **options: t.Any) -> None:
        code.interact(local=locals())

        return None
