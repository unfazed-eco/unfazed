import typing as t
from importlib import import_module

from .routing import Mount, Route, Static
from .websocket_routing import WebSocketRoute

if t.TYPE_CHECKING:
    from unfazed.app import AppCenter  # pragma: no cover


T = t.Union[Route, WebSocketRoute, t.List["T"]]


def _flatten_patterns(patterns: t.List[T]) -> t.List[t.Union[Route, WebSocketRoute]]:
    flat_patterns: t.List[t.Union[Route, WebSocketRoute]] = []
    for pattern in patterns:
        if isinstance(pattern, t.List):
            flat_patterns.extend(_flatten_patterns(pattern))
        elif isinstance(pattern, (Route, WebSocketRoute)):
            flat_patterns.append(pattern)
        else:
            continue
    return flat_patterns


def parse_urlconf(
    root_urlconf: str, app_center: "AppCenter"
) -> t.List[t.Union[Route, WebSocketRoute, Static, Mount]]:
    """
    Unfazed parse routes from ROOT_URLCONF
    and will flatten the patterns and return a list of Route, Static, Mount

    """
    ret: t.List[t.Union[Route, WebSocketRoute, Static, Mount]] = []
    root_url_module = import_module(root_urlconf)
    if not hasattr(root_url_module, "patterns"):
        raise ValueError(f"ROOT_URLCONF {root_urlconf} should have patterns defined")

    module_patterns = t.cast(t.List[T], root_url_module.patterns)
    patterns = _flatten_patterns(module_patterns)

    for route in patterns:
        if isinstance(route, (Static, Mount)):
            ret.append(route)
            continue
        if isinstance(route, WebSocketRoute):  # pragma: no cover
            ret.append(route)
            continue
        if route.app_label and route.app_label not in app_center:
            raise ValueError(f"App {route.app_label} is not installed")

        ret.append(route)

    return ret
