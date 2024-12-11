import typing as t

from unfazed.protocol import DataBaseDriver
from unfazed.schema import Database
from unfazed.utils import import_string

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class ModelCenter:
    def __init__(self, unfazed: "Unfazed", conf: Database | None) -> None:
        self.unfazed = unfazed
        self.conf = conf

    async def setup(self) -> None:
        if not self.conf:
            return
        driver_cls = import_string(self.conf.driver)
        driver: DataBaseDriver = driver_cls(self.unfazed, self.conf)
        await driver.setup()

        self.driver = driver

    async def migrate(self) -> None:
        await self.driver.migrate()
