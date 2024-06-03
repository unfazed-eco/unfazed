from typing import Any

from databases import Database
from databases.core import DatabaseURL


class DataBaseWapper(Database):
    def __init__(
        self, url: str | DatabaseURL, *, force_rollback: bool = False, **options: Any
    ):
        super().__init__(url, force_rollback=force_rollback, **options)
