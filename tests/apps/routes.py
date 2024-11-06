from unfazed.route import include, path

patterns = [path("/api/admin", routes=include("unfazed.contrib.admin.routes"))]
