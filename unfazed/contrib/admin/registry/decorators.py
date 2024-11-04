import typing as t
from functools import wraps

from unfazed.db.tortoise.serializer import TSerializer

from .collector import admin_collector
from .models import BaseModel


class ActionOutput:
    Download = 1
    Refresh = 2
    Toast = 3
    Jump = 4
    Table = 5


def register(serializer_cls: t.Type[TSerializer]):
    def wrapper(admin_cls: t.Type[BaseModel]):
        admin_ins = admin_cls()
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
    *,
    extra: t.Dict[str, t.Any] = {},
):
    def wrapper(method: t.Callable):
        @wraps(method)
        def inner(*args, **kwargs):
            return method(*args, **kwargs)

        method.action = True
        method.attrs = {
            "name": name or method.__name__,
            "output": output,
            "confirm": confirm,
            "description": description,
            **extra,
        }

        return inner

    return wrapper


def batch_action(
    name: str | None = None,
    output: t.Literal[1, 2, 3, 4, 5] = ActionOutput.Toast,
    confirm: bool = False,
    description: str = "",
    *,
    extra: t.Dict[str, t.Any] = {},
):
    def wrapper(method: t.Callable):
        @wraps(method)
        def inner(*args, **kwargs):
            return method(*args, **kwargs)

        method.batch_action = True
        method.attrs = {
            "name": name or method.__name__,
            "output": output,
            "confirm": confirm,
            "description": description,
            **extra,
        }

        return inner

    return wrapper
