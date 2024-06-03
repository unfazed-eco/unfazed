import typing as t

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed

from unfazed.protocol import OrmModel


class ModelCenter:
    def __init__(
        self,
        unfazed: "Unfazed",
        models: t.List[t.Type[OrmModel]] | None = None,
    ) -> None:
        self.unfazed = unfazed
        self.models = models

    def add_model(self, model: t.Type[OrmModel]) -> None:
        if self.models is None:
            self.models = []
        self.models.append(model)
