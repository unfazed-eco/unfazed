from unfazed.route import include, path

patterns = [path("/api/contrib/admin", routes=include("unfazed.contrib.admin.routes"))]
