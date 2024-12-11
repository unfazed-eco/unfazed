import typing as t
from asyncio import Lock

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


def unfazed_locker(async_method: t.Callable) -> t.Callable:
    """
    Docorator to help Unfazed to lock the method until it's ready.

    """

    async def wrapper(self: "Unfazed", *args: t.Any, **kwargs: t.Any) -> t.Any:
        if self._ready:
            return
        async with Lock():
            if self._ready:
                return  # pragma: no cover

            if self._loading:
                raise RuntimeError("Unfazed is already loading")

            self._loading = True

            ret = await async_method(self, *args, **kwargs)

            self._ready = True
            self._loading = False

            return ret

    return wrapper
