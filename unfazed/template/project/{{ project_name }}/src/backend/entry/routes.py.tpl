from unfazed.route import path

"""

example:

patterns = [
    path("/index", endpoint="index"),
    path("/api/account", routes=include("account.routes")),
    path("/api/auth", routes=patterns),
]


"""


patterns = []

