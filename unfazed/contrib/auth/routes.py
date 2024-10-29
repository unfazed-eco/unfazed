from unfazed.route import path

from .endpoints import login, logout

patterns = [
    path("/login", endpoint=login, name="unfazed_auth_login"),
    path("/logout", endpoint=logout, name="unfazed_auth_logout"),
]
