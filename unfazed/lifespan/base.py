import typing as t

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover


class BaseLifeSpan:
    """
    Base LifeSpan class

    reference(what is lifespan):
        https://asgi.readthedocs.io/en/latest/specs/lifespan.html

    Uasge:
    ```python


    class MyLifeSpan(BaseLifeSpan):
        async def on_startup(self) -> None:
            # get app settings
            settings = self.unfazed.settings
            # do something
            # when app start up

            # connection.start()

            ...

        async def on_shutdown(self) -> None:
            # do something
            # when app shutdown

            # connection.close()

            ...
    ```

    """

    def __init__(self, unfazed: "Unfazed") -> None:
        self.unfazed = unfazed

    async def on_startup(self) -> None:
        return None

    async def on_shutdown(self) -> None:
        return None

    @property
    def state(self) -> t.Dict[str, t.Any]:
        return {}
