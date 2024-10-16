from unfazed.route import include, path

patterns = [
    path("/api/account", routes=include("account.routes")),
    path("/api/student", routes=include("student.routes")),
]
