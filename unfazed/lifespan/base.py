import typing as t

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class BaseLifeSpan:
    """Base class for managing component lifecycle in Unfazed framework.

    This class provides a standardized interface for handling component lifecycle events
    in the Unfazed framework. It follows the ASGI lifespan protocol specification
    (https://asgi.readthedocs.io/en/latest/specs/lifespan.html) and allows components
    to perform initialization and cleanup operations during application startup and shutdown.

    The lifecycle consists of two main events:
    1. Startup: Called when the application starts, used for resource initialization
    2. Shutdown: Called when the application shuts down, used for resource cleanup

    Attributes:
        unfazed (Unfazed): The Unfazed application instance this lifespan component belongs to.

    Example:
        ```python
        class DatabaseLifeSpan(BaseLifeSpan):
            async def on_startup(self) -> None:
                # Initialize database connection
                self.db = await create_connection(self.unfazed.settings.database_url)
                # Store connection in state for other components to use
                self._state["db"] = self.db

            async def on_shutdown(self) -> None:
                # Clean up database connection
                if hasattr(self, "db"):
                    await self.db.close()

            @property
            def state(self) -> t.Dict[str, t.Any]:
                return self._state
        ```

    Note:
        - All lifecycle methods are asynchronous to support non-blocking operations
        - The state property can be used to share data between different lifespan components
        - Error handling should be implemented in the concrete classes
    """

    def __init__(self, unfazed: "Unfazed") -> None:
        """Initialize the lifespan component.

        Args:
            unfazed: The Unfazed application instance.
        """
        self.unfazed = unfazed

    async def on_startup(self) -> None:
        """Handle application startup event.

        This method is called when the application starts. Override this method to
        perform initialization tasks such as:
        - Establishing database connections
        - Loading configuration
        - Initializing caches
        - Setting up external service connections

        Returns:
            None
        """
        return None

    async def on_shutdown(self) -> None:
        """Handle application shutdown event.

        This method is called when the application shuts down. Override this method to
        perform cleanup tasks such as:
        - Closing database connections
        - Flushing caches
        - Closing external service connections
        - Saving application state

        Returns:
            None
        """
        return None

    @property
    def state(self) -> t.Dict[str, t.Any]:
        """Get the component's state.

        This property should be overridden to return a dictionary containing the
        component's state that needs to be shared with other components.

        Returns:
            A dictionary containing the component's state.
        """
        return {}
