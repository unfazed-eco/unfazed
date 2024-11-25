from unfazed.route import path

from .endpoints import login, logout, register

patterns = [
    path("/login", endpoint=login, name="unfazed_auth_login", methods=["POST"]),
    path("/logout", endpoint=logout, name="unfazed_auth_logout", methods=["POST"]),
    path(
        "/register", endpoint=register, name="unfazed_auth_register", methods=["POST"]
    ),
]
