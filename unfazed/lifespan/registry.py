import logging
import typing as t
from contextlib import asynccontextmanager

from unfazed.type import ASGIApp

from .base import BaseLifeSpan

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover

logger = logging.getLogger("unfazed.setup")


class State(t.Dict[str, t.Any]):
    """A dictionary-like class to store application state."""

    pass


class LifeSpanHandler:
    """
    Handles the lifecycle events (startup and shutdown) for various components.

    This class manages the registration and execution of lifespan events for different
    parts of the application.
    """

    def __init__(self) -> None:
        """Initialize the lifespan handler with empty collections."""
        self.lifespan: t.Dict[str, BaseLifeSpan] = {}
        self.unfazed: "Unfazed" | None = None

    def register(self, name: str, lifespan: BaseLifeSpan) -> None:
        """
        Register a new lifespan component.

        Args:
            name: The name of the lifespan component
            lifespan: The lifespan component to register

        Raises:
            ValueError: If a lifespan with the same name is already registered
        """
        if name in self.lifespan:
            raise ValueError(f"Lifespan component '{name}' is already registered")
        self.lifespan[name] = lifespan

    def get(self, name: str) -> BaseLifeSpan | None:
        """
        Get a registered lifespan component by name.

        Args:
            name: The name of the lifespan component

        Returns:
            The lifespan component if found, None otherwise
        """
        return self.lifespan.get(name)

    async def on_startup(self) -> None:
        """
        Execute the startup event for all registered lifespan components.

        This method is called when the application starts.
        """
        for _, lifespan in self.lifespan.items():
            try:
                await lifespan.on_startup()
            except Exception as e:
                # Log the error but continue with other components
                logger.error(f"Error during startup: {e}")
                raise e

    async def on_shutdown(self) -> None:
        """
        Execute the shutdown event for all registered lifespan components.

        This method is called when the application shuts down.
        """
        for _, lifespan in self.lifespan.items():
            try:
                await lifespan.on_shutdown()
            except Exception as e:
                # Log the error but continue with other components
                logger.error(f"Error during shutdown: {e}")
                raise e

    @property
    def state(self) -> State:
        """
        Get the combined state from all lifespan components.

        Returns:
            A State object containing the combined state
        """
        ret = State()
        for _, lifespan in self.lifespan.items():
            ret.update(lifespan.state)
        return ret

    def clear(self) -> None:
        """Clear all registered lifespan components."""
        self.lifespan.clear()


# Global instance of the lifespan handler
handler = LifeSpanHandler()


@asynccontextmanager
async def lifespan(app: ASGIApp) -> t.AsyncIterator[State]:
    """
    ASGI lifespan context manager.

    This function is used as a lifespan context manager for ASGI applications.
    It handles the startup and shutdown events for all registered lifespan components.

    Args:
        app: The ASGI application

    Yields:
        The application state
    """
    await handler.on_startup()
    yield handler.state
    await handler.on_shutdown()
