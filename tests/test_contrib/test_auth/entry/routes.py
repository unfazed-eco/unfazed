from unfazed.route import include, path

patterns = [
    path("/api/contrib/auth", routes=include("unfazed.contrib.auth.routes")),
]
