import logging
import typing as t

from unfazed.protocol import DataBaseDriver
from unfazed.schema import Database
from unfazed.utils import import_string

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover

logger = logging.getLogger("unfazed.setup")


class ModelCenter:
    """
    ModelCenter is a registry for orm pkg.
    It manages the database driver lifecycle and provides database operations.
    """

    def __init__(self, unfazed: "Unfazed", conf: Database | None) -> None:
        self.unfazed = unfazed
        self.conf = conf
        self.driver: DataBaseDriver | None = None

    async def setup(self) -> None:
        """Setup the database driver with the given configuration."""
        if not self.conf:
            logger.debug("No database configuration provided, skipping setup")
            return

        driver_cls = import_string(self.conf.driver)
        driver: DataBaseDriver = driver_cls(self.unfazed, self.conf)
        await driver.setup()
        self.driver = driver
        logger.debug("Database driver setup completed successfully")

    async def migrate(self) -> None:
        """
        Migrate all models to database.
        Better using this in test case.
        """
        if self.driver is None:
            raise ValueError("driver not setup")  # type: ignore
        await self.driver.migrate()
