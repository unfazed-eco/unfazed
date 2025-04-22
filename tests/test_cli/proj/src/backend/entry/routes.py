"""

example:

patterns = [
    path("/index", endpoint="index"),
    path("/api/account", routes=include("account.routes")),
    path("/api/auth", routes=patterns),
]


"""

import typing as t

from unfazed.route import Route

patterns: t.List[Route] = []
