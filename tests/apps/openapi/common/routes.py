from unfazed.route import path

from . import endpoints as E

patterns = [
    path("/account-list", endpoint=E.list_account),
    path("/account-create", endpoint=E.create_account, methods=["POST"]),
    path("/account-update", endpoint=E.update_account, methods=["POST"]),
    path("/account-delete", endpoint=E.delete_account, methods=["POST"]),
    path("/account/{user_id}", endpoint=E.retrieve_account, methods=["POST"]),
]
