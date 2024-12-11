import os
import typing as t
from importlib import import_module


def import_string(name: str) -> t.Type:
    """
    Import a class or object from a module using its fully qualified name.

    Raises:
    ImportError: If the module path is invalid or the module cannot be imported.

    Example:
    >>> import_string("unfazed.http.HttpResponse")
    <class 'unfazed.http.HttpResponse'>

    """

    try:
        module_name, class_name = name.rsplit(".", 1)
    except ValueError:
        raise ImportError(f"{name} doesn't look like a module path")

    module = import_module(module_name)
    return getattr(module, class_name)


def import_setting(env: str) -> t.Dict[str, t.Any]:
    """
    Import the settings module specified by the environment variable `env`.

    Raises:
    ValueError: If the environment variable is not set.
    ImportError: If the settings module cannot be imported.

    Example:
    >>> import_setting("UNFAZED_SETTINGS_MODULE")
    """
    settings_module = os.environ.get(env)
    if not settings_module:
        raise ValueError(f"environment variable {env} is not set")
    try:
        settingskv = import_module(settings_module).__dict__
    except ImportError:
        raise ImportError(f"Could not import settings module {settings_module}")

    return settingskv
