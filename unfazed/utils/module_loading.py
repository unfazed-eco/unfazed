import os
import typing as t
from importlib import import_module


def import_string(name: str) -> t.Type:
    """
    Import a class or object from a module using its fully qualified name.
    Args:
        name (str): The fully qualified name of the class or object to import.
    Returns:
        Type: The imported class or object.
    Raises:
        ImportError: If the name doesn't look like a valid module path.
    Example:
        >>> import_string('path.to.module.ClassName')
        <class 'path.to.module.ClassName'>
    """

    try:
        module_name, class_name = name.rsplit(".", 1)
    except ValueError:
        raise ImportError(f"{name} doesn't look like a module path")

    module = import_module(module_name)
    return getattr(module, class_name)


def import_setting(env: str) -> t.Mapping[str, t.Any]:
    """
    Import the settings module specified by the environment variable `env`.
    Args:
        env (str): The name of the environment variable containing the settings module.
    Returns:
        Mapping[str, Any]: A dictionary-like object containing the settings module's attributes.
    Raises:
        Exception: If the environment variable `env` is not set.
        ImportError: If the settings module specified by the environment variable `env` cannot be imported.
    """
    settings_module = os.environ.get(env)
    print("settings_module", settings_module)
    if not settings_module:
        raise ValueError(f"environment variable {env} is not set")
    try:
        settingskv = import_module(settings_module).__dict__
    except ImportError:
        raise ImportError(f"Could not import settings module {settings_module}")

    return settingskv
