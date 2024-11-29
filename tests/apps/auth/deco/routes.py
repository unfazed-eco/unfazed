from unfazed.route import path

from . import endpoints as e

patterns = [
    path(
        "/async-login-succeed",
        endpoint=e.async_login_succeed,
        name="async_login_succeed",
        methods=["GET"],
    ),
    path(
        "/login-succeed",
        endpoint=e.login_succeed,
        name="login_succeed",
        methods=["GET"],
    ),
    path(
        "/async-login-fail",
        endpoint=e.async_login_fail,
        name="async_login_fail",
        methods=["GET"],
    ),
    path("/login-fail", endpoint=e.login_fail, name="login_fail", methods=["GET"]),
    path(
        "/async-permission-succeed",
        endpoint=e.async_permission_succeed,
        name="async_permission_succeed",
        methods=["GET"],
    ),
    path(
        "/permission-succeed",
        endpoint=e.permission_succeed,
        name="permission_succeed",
        methods=["GET"],
    ),
    path(
        "/async-permission-fail",
        endpoint=e.async_permission_fail,
        name="async_permission_fail",
        methods=["GET"],
    ),
    path(
        "/permission-fail",
        endpoint=e.permission_fail,
        name="permission_fail",
        methods=["GET"],
    ),
]
