import typing as t
from importlib import import_module

from .routing import Route

if t.TYPE_CHECKING:
    from unfazed.app import AppCenter  # pragma: no cover


def _flatten_patterns(
    patterns: t.Sequence[Route | t.Sequence[Route]],
) -> t.Sequence[Route]:
    flat_patterns = []
    for pattern in patterns:
        if isinstance(pattern, list):
            flat_patterns.extend(_flatten_patterns(pattern))
        else:
            flat_patterns.append(pattern)
    return flat_patterns


def parse_urlconf(root_urlconf: str, app_center: "AppCenter") -> t.List[Route]:
    ret = []
    root_url_module = import_module(root_urlconf)
    if not hasattr(root_url_module, "patterns"):
        raise ValueError(f"ROOT_URLCONF {root_urlconf} should have patterns defined")

    patterns = _flatten_patterns(root_url_module.patterns)

    for route in patterns:
        if route.app_label and route.app_label not in app_center:
            raise ValueError(f"App {route.app_label} is not installed")

        ret.append(route)

    return ret
