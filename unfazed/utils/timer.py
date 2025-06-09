import logging
import time
import typing as t
from types import TracebackType

logger = logging.getLogger("unfazed.utils.timer")


class Timer:
    """
    Timer for measuring the time taken to execute a block of code.

    Example:
        ```python
        with Timer("setup_unfazed"):
            self.setup_logging()
        ```
    """

    def __init__(self, name: str) -> None:
        self.start_time = time.time()
        self.name = name

    def __enter__(self) -> None:
        self.start_time = time.time()

    def __exit__(
        self,
        exc_type: t.Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        self.end_time = time.time()
        logger.debug(
            f"{self.name} Time taken: {self.end_time - self.start_time} seconds"
        )
