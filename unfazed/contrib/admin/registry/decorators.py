import inspect
import typing as t
from functools import wraps

from unfazed.serializer.tortoise import TSerializer

from .collector import admin_collector
from .schema import AdminAction

if t.TYPE_CHECKING:
    from .models import BaseAdmin  # pragma: no cover


class ActionOutput:
    Download = 1
    Refresh = 2
    Toast = 3
    Jump = 4
    Table = 5


def register(serializer_cls: t.Type[TSerializer] | None = None):
    def wrapper(admin_cls: t.Type["BaseAdmin"]):
        admin_ins = admin_cls()
        if serializer_cls:
            admin_ins.serializer = serializer_cls
        override = getattr(admin_cls, "override", False)
        admin_collector.set(admin_ins.name, admin_ins, override=override)

        return admin_cls

    return wrapper


def action(
    name: str | None = None,
    output: t.Literal[1, 2, 3, 4, 5] = ActionOutput.Toast,
    confirm: bool = False,
    description: str = "",
    batch: bool = False,
    *,
    extra: t.Dict[str, t.Any] = {},
):
    def wrapper(method: t.Callable):
        @wraps(method)
        async def asyncinner(*args, **kwargs):
            return await method(*args, **kwargs)

        @wraps(method)
        def inner(*args, **kwargs):
            return method(*args, **kwargs)

        attrs = AdminAction(
            name=name or method.__name__,
            raw_name=method.__name__,
            output=output,
            confirm=confirm,
            description=description,
            batch=batch,
            extra=extra,
        )

        if inspect.iscoroutinefunction(method):
            setattr(asyncinner, "action", True)
            setattr(asyncinner, "attrs", attrs)
            return asyncinner
        else:
            setattr(inner, "action", True)
            setattr(inner, "attrs", attrs)
            return inner

    return wrapper
