from unfazed.protocol import OrmQuerySet


class QuerySet(OrmQuerySet):
    def __init__(self) -> None:
        self._using = "default"

    def using(self, alias: str):
        self._using = alias
        return self

    def filter(self, **kwargs):
        return self

    def exclude(self, **kwargs):
        return self

    async def all(self):
        return self

    async def get(self, **kwargs):
        return self

    async def create(self, **kwargs):
        return self

    async def update(self, **kwargs):
        return self

    async def delete(self, **kwargs):
        return self

    async def bulk_create(self, **kwargs):
        return self

    async def get_or_create(self, **kwargs):
        return self

    async def update_or_create(self, **kwargs):
        return self

    async def execute(self):
        return self
