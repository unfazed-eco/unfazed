import asyncio
import typing as t

from click import Command as ClickCommand
from click import Parameter

from unfazed.protocol import Command

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class BaseCommand(ClickCommand, Command):
    help_text = ""

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
        if not asyncio.iscoroutinefunction(self.handle):
            raise TypeError("handle method must be a coroutine")
        asyncio.run(self.handle(**option))

    def add_arguments(self) -> t.List[Parameter | None]:
        return []

    async def handle(self, **option: t.Any) -> None:
        raise NotImplementedError("handle method must be implemented")
