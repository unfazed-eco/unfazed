import typing as t

from unfazed.route import Route, include, path

patterns: t.List[Route] = [
    path("/api/admin", routes=include("unfazed.contrib.admin.routes")),
    path("/api/auth", routes=include("unfazed.contrib.auth.routes")),
]
