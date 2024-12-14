import asyncio
import typing as t
from abc import ABC, abstractmethod

from click import Command as ClickCommand
from click import Option, Parameter

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class BaseCommand(ClickCommand, ABC):
    """
    Base class for all commands.

    Usage:
    ```python

    from unfazed.command import BaseCommand
    from click import Option

    class Command(BaseCommand):
        help_text = "This is a command"
        def add_arguments(self) -> t.List[Option]:
            return [
                Option(
                    ["--host"],
                    type=str,
                    help="The host to listen on",
                    default="")
                ]

        async def handle(self, **option: t.Any) -> None:

            host = option["host"]
            print(f"Host: {host}")

    # >>> python manage.py {command} --host 0.0.0.0

    ```

    """

    help_text = ""

    @t.override
    def __init__(
        self,
        unfazed: "Unfazed",
        name: str,
        app_label: str,
        *,
        context_settings: t.MutableMapping[str, t.Any] | None = None,
        callback: t.Callable[..., t.Any] | None = None,
        params: t.List[Parameter] | None = None,
        help: str | None = None,
        epilog: str | None = None,
        short_help: str | None = None,
        options_metavar: str | None = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
    ) -> None:
        help = help or self.help_text
        params = params or []
        params.extend(self.add_arguments())
        callback = self._callback

        self.unfazed = unfazed
        self.app_label = app_label

        super().__init__(
            name,
            context_settings,
            callback,
            params,
            help,
            epilog,
            short_help,
            options_metavar,
            add_help_option,
            no_args_is_help,
            hidden,
            deprecated,
        )

    def _callback(self, **option: t.Optional[t.Any]) -> None:
        if asyncio.iscoroutinefunction(self.handle):
            asyncio.run(self.handle(**option))
        else:
            # due to handle must be implemented as a coroutine
            # so this branch will never be reached
            # just for type checking
            raise NotImplementedError(
                "handle method must be a coroutine"
            )  # pragma: no cover

    def add_arguments(self) -> t.List[Option]:
        return []

    @abstractmethod
    async def handle(self, **option: t.Any) -> None: ...
