from unfazed.route import path

from .endpoints import login, logout, register

patterns = [
    path("/login", endpoint=login, name="unfazed_auth_login"),
    path("/logout", endpoint=logout, name="unfazed_auth_logout"),
    path("/register", endpoint=register, name="unfazed_auth_register"),
]
