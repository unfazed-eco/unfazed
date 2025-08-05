from unfazed.route import path

from .endpoints import login, logout, register

patterns = [
    path(
        "/login",
        endpoint=login,
        name="unfazed_auth_login",
        methods=["POST"],
        operation_id="login",
    ),
    path(
        "/logout",
        endpoint=logout,
        name="unfazed_auth_logout",
        methods=["POST"],
        operation_id="logout",
    ),
    path(
        "/register",
        endpoint=register,
        name="unfazed_auth_register",
        methods=["POST"],
        operation_id="register",
    ),
]
