import typing as t
import warnings

from tortoise.models import Model as _Model

if t.TYPE_CHECKING:
    from tortoise.backends.base.client import BaseDBAsyncClient
    from tortoise.signals import Signals


class Model(_Model):
    """
    inherit from tortoise.models.Model
    but disable all signals

    """

    _listeners = {}

    @t.final
    @classmethod
    def register_listener(cls, signal: "Signals", listener: t.Callable) -> None:
        warnings.warn("Signal is not allowed in unfazed", UserWarning)
        return

    @t.final
    async def _wait_for_listeners(self, signal: "Signals", *listener_args) -> None:
        warnings.warn("Signal is not allowed in unfazed", UserWarning)
        return

    @t.final
    async def _pre_delete(
        self, using_db: t.Optional["BaseDBAsyncClient"] = None
    ) -> None:
        warnings.warn("Signal is not allowed in unfazed", UserWarning)
        return

    @t.final
    async def _post_delete(
        self, using_db: t.Optional["BaseDBAsyncClient"] = None
    ) -> None:
        warnings.warn("Signal is not allowed in unfazed", UserWarning)
        return

    @t.final
    async def _pre_save(
        self,
        using_db: t.Optional["BaseDBAsyncClient"] = None,
        update_fields: t.Optional[t.Iterable[str]] = None,
    ) -> None:
        warnings.warn("Signal is not allowed in unfazed", UserWarning)
        return

    @t.final
    async def _post_save(
        self,
        using_db: t.Optional["BaseDBAsyncClient"] = None,
        created: bool = False,
        update_fields: t.Optional[t.Iterable[str]] = None,
    ) -> None:
        warnings.warn("Signal is not allowed in unfazed", UserWarning)
        return

