from unfazed.route import path

from .endpoints import login, login_redirect, logout, logout_redirect, register

patterns = [
    path("/login", endpoint=login, name="unfazed_auth_login"),
    path("/logout", endpoint=logout, name="unfazed_auth_logout"),
    path("/register", endpoint=register, name="unfazed_auth_register"),
    path("/oauth/login", endpoint=login_redirect, name="unfazed_oauth_login"),
    path("/oauth/logout", endpoint=logout_redirect, name="unfazed_oauth_logout"),
]
