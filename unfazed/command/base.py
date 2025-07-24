import asyncio
import logging
import typing as t
from abc import ABC, abstractmethod

from click import Command as ClickCommand
from click import Option, Parameter

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


logger = logging.getLogger("unfazed.command")


class BaseCommand(ClickCommand, ABC):
    """
    Base class for all commands in the Unfazed framework.

    This class extends Click's Command class and provides a foundation for creating
    command-line interfaces with async support. It handles the integration between
    Click's synchronous command execution and asynchronous command handlers.

    Key features:
    - Async command handling with automatic coroutine execution
    - Automatic argument management
    - Integration with Unfazed application context
    - Type-safe command implementation

    Usage:
    ```python
    from unfazed.command import BaseCommand
    from click import Option

    class MyCommand(BaseCommand):
        help_text = "This is a command that does something"

        def add_arguments(self) -> t.List[Option]:
            return [
                Option(
                    ["--host"],
                    type=str,
                    help="The host to listen on",
                    default="localhost"
                ),
                Option(
                    ["--port"],
                    type=int,
                    help="The port to listen on",
                    default=8000
                )
            ]

        async def handle(self, **options: t.Any) -> None:
            host = options["host"]
            port = options["port"]
            logger.info(f"Starting server on {host}:{port}")
            # Command implementation here

    # Usage: unfazed-cli my-command --host 0.0.0.0 --port 8080
    ```

    Attributes:
        help_text (str): Default help text for the command
        unfazed (Unfazed): Reference to the Unfazed application instance
        app_label (str): Label identifying the application this command belongs to
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
        """
        Initialize a new command instance.

        Args:
            unfazed: The Unfazed application instance
            name: The command name
            app_label: The application label this command belongs to
            context_settings: Optional Click context settings
            callback: Optional callback function (not used, handled internally)
            params: Optional list of Click parameters
            help: Optional help text
            epilog: Optional epilog text
            short_help: Optional short help text
            options_metavar: Optional options metavar string
            add_help_option: Whether to add the help option
            no_args_is_help: Whether to show help when no args are provided
            hidden: Whether the command should be hidden
            deprecated: Whether the command is deprecated
        """
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

    def _callback(self, **options: t.Optional[t.Any]) -> None:
        """
        Internal callback that handles the execution of the handle method.

        Supports both synchronous and asynchronous handle methods:
        - If handle is a coroutine function, runs it with asyncio.run()
        - If handle is a regular function, calls it directly

        Args:
            **options: Command options passed from Click
        """

        if asyncio.iscoroutinefunction(self.handle):
            # Handle async method
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.handle(**options))
        else:
            # Handle sync method
            self.handle(**options)

    def add_arguments(self) -> t.List[Option]:
        """
        Add command-specific arguments.

        Override this method to add custom command arguments.
        The default implementation returns an empty list.

        Returns:
            A list of Click Option objects
        """
        return []

    @abstractmethod
    def handle(self, **options: t.Any) -> t.Any:
        """
        Handle the command execution.

        This method must be implemented by all command subclasses.
        It contains the main command logic and can be either synchronous or asynchronous.

        For async commands:
        ```python
        async def handle(self, **options: t.Any) -> None:
            await some_async_operation()
        ```

        For sync commands:
        ```python
        def handle(self, **options: t.Any) -> None:
            some_sync_operation()
        ```

        Args:
            **options: Command options passed from Click

        Returns:
            Any: Optional return value from the command

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        ...  # pragma: no cover
