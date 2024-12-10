import inspect
import typing as t
from functools import wraps

from unfazed.serializer import Serializer

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


def register(serializer_cls: t.Type[Serializer] | None = None) -> t.Callable:
    def wrapper(admin_cls: t.Type["BaseAdmin"]) -> t.Type["BaseAdmin"]:
        admin_ins = admin_cls()
        if serializer_cls:
            admin_ins.serializer = serializer_cls  # type: ignore
        override = getattr(admin_cls, "override", False)
        admin_collector.set(admin_ins.name, admin_ins, override=override)

        return admin_cls

    return wrapper


def action(
    name: str | None = None,
    output: int = ActionOutput.Toast,
    confirm: bool = False,
    description: str = "",
    batch: bool = False,
    *,
    extra: t.Dict[str, t.Any] = {},
) -> t.Callable:
    def wrapper(method: t.Callable) -> t.Callable:
        @wraps(method)
        async def asyncinner(*args: t.Any, **kwargs: t.Any) -> t.Any:
            return await method(*args, **kwargs)

        @wraps(method)
        def inner(*args: t.Any, **kwargs: t.Any) -> t.Any:
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
