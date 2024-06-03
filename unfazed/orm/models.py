import typing as t

from pydantic import BaseModel, ConfigDict

from unfazed.protocol import OrmMeta

# type hinting
_ = t.Optional
M = t.TypeVar("M", bound="Model")
Ins = t.TypeVar("Ins", bound="BaseModel")


class Meta(OrmMeta):
    def __init__(
        self,
        db_table: _[str] = None,
        abstract: bool = False,
        app_label: _[str] = None,
        db_table_comment: _[str] = "",
        default_order_by: _[list[str]] = None,
        indexes: _[list[str]] = None,
        unique_together: _[list[str]] = None,
    ):
        self._db_table = db_table
        self.abstract = abstract
        self._app_label = app_label
        self.db_table_comment = db_table_comment
        self.default_order_by = default_order_by
        self.indexes = indexes
        self.unique_together = unique_together

        self._database = None
        self._model: M = None

    def set_database(self, database):
        self._database = database

    def set_model(self, model: t.Type[M]):
        self._model = model

    @property
    def db_table(self):
        if not self._db_table:
            self._db_table = f"{self.app_label}_{self._model.__name__.lower()}"
        return self._db_table

    @property
    def app_label(self):
        if not self._app_label:
            self._app_label = self._model.__module__.split(".")[-2]
        return self._app_label

    def build_table(self):
        pass


class Model(BaseModel):
    """

    Usage:

    ```python

    from unfazed_orm.models import Model, Meta

    class User(Model):
        meta = Meta(db_table="users")

    """

    meta: Meta
    # objects = QuerySet()
    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def save(self):
        return self

    async def delete(self):
        return self

    async def load(self):
        return self
