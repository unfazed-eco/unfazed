from unfazed.route import path

from .views import create_user, list_user

patterns = [
    path("/user-list", endpoint=list_user),
    path("/user-create", endpoint=create_user),
]
