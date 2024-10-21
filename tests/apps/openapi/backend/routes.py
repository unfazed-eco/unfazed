from unfazed.route import include, path

patterns = [
    path("/api/account", routes=include("common.routes")),
]
