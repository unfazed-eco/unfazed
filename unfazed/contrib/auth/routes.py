from unfazed.route import path

from .endpoints import (
    login,
    logout,
    oauth_login_redirect,
    oauth_logout_redirect,
    register,
)

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
    path(
        "/oauth-login-redirect",
        endpoint=oauth_login_redirect,
        name="unfazed_auth_oauth_login_redirect",
        methods=["GET"],
        operation_id="oauth_login_redirect",
    ),
    path(
        "/oauth-logout-redirect",
        endpoint=oauth_logout_redirect,
        name="unfazed_auth_oauth_logout_redirect",
        methods=["GET"],
        operation_id="oauth_logout_redirect",
    ),
]
