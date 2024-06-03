import typing as t
from importlib import import_module


def import_string(import_name: str) -> t.Type:
    """
    Import a class or object from a string representing the module path and object name.

    Args:
        import_name (str): The string representing the module path and object name.

    Returns:
        Type: The imported class or object.

    Raises:
        ImportError: If the import_name doesn't look like a valid module path.
    """
    try:
        module_name, class_name = import_name.rsplit(".", 1)
    except ValueError:
        raise ImportError(f"{import_name} doesn't look like a module path")

    module = import_module(module_name)
    return getattr(module, class_name)
