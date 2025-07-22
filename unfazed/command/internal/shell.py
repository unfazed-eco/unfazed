import typing as t

from IPython import start_ipython

from unfazed.command import BaseCommand


class Command(BaseCommand):
    """
    Currently, unfazed only support default python shell

    Ipython not supported yet

    """

    help_text = """Run the unfazed Shell use ipython

    Usage:

    >>> unfazed-cli shell
    """

    def handle(self, **options: t.Any) -> None:
        user_ns: t.Dict[str, t.Any] = {
            "unfazed": self.unfazed,
        }
        startup_code: t.List[str] = [
            "import asyncio",
            "print('🚀 Unfazed Shell - Asyncio enabled!')",
            "print('💡 You can use await directly in the shell')",
            "print(f'Unfazed APP: {unfazed}')",
            "print(f'💡 You can use `unfazed` instance directly in the shell')",
        ]
        start_ipython(argv=[], user_ns=user_ns, exec_lines=startup_code)  # type: ignore
