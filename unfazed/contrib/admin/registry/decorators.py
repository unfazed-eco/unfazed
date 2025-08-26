import inspect
import typing as t
from functools import wraps

from unfazed.serializer import Serializer

from .collector import admin_collector
from .schema import ActionInput, ActionKwargs, ActionOutput, AdminAction

if t.TYPE_CHECKING:
    from .models import BaseAdmin  # pragma: no cover


def register(serializer_cls: t.Type[Serializer] | None = None) -> t.Callable:
    """Register an admin class in the admin collector.

    Args:
        serializer_cls: The serializer class to use for the admin.


    Usage:
        ```python
        @register(UserSerializer)
        class UserAdmin(ModelAdmin):
            pass

        @register(GroupSerializer)
        class GroupAdmin(ModelAdmin):
            pass
        ```
    """

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
    label: str | None = None,
    output: ActionOutput = ActionOutput.Toast,
    input: ActionInput = ActionInput.Empty,
    confirm: bool = False,
    description: str = "",
    batch: bool = False,
    *,
    extra: t.Dict[str, t.Any] = {},
) -> t.Callable:
    """
    Register an action for the admin.

    Args:
        name: The name of the action.
        label: The label of the action displayed in the UI.
        input: The input type of the action.
        output: The output type of the action.
        confirm: Whether to confirm the action.
        description: The description of the action.
        batch: Whether the action is a batch action.
        extra: Extra arguments for the action.

    Usage:
        ```python
        @action(name="export", label="Export", output=ActionOutput.Download)
        async def export(self, ctx: ActionKwargs) -> str:
            return "export"
        ```
    """

    def wrapper(method: t.Callable) -> t.Callable:
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        if len(params) != 2:
            raise ValueError(
                f"Action method '{method.__name__}' must have exactly 2 parameters, self and ctx: ActionKwargs"
            )

        @wraps(method)
        async def asyncinner(self: "BaseAdmin", ctx: ActionKwargs) -> t.Any:
            return await method(self, ctx)

        @wraps(method)
        def inner(self: "BaseAdmin", ctx: ActionKwargs) -> t.Any:
            return method(self, ctx)

        attrs = AdminAction(
            name=name or method.__name__,
            label=label or method.__name__,
            output=output,
            input=input,
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
