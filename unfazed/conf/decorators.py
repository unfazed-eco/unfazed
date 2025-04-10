import typing as t

from pydantic import BaseModel

from .base import settings


def register_settings(key: str) -> t.Callable[[t.Type[BaseModel]], t.Type[BaseModel]]:
    """
    Decorator to register a settings class with the settings module.

    Args:
        key: The key to register the settings under in the settings module.

    Usage:

    ```python
    @register_settings("MY_SETTINGS")
    class MySettings(BaseModel):
        foo: str
        bar: int
    ```

    ```python
    # settings.py
    MY_SETTINGS = {
        "foo": "bar",
        "bar": 1,
    }
    ```

    ```python
    from unfazed.conf import settings
    my_settings: MySettings = settings["MY_SETTINGS"]
    ```

    """

    def decorator(cls: t.Type[BaseModel]) -> t.Type[BaseModel]:
        settings.register_client_cls(key, cls)

        return cls

    return decorator
