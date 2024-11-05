from unfazed.route import path

from . import endpoints as e

patterns = [
    path("/route-list", endpoint=e.list_route, name="route-list"),
    path("/settings", endpoint=e.settings, name="settings"),
    path(
        "/model-desc",
        endpoint=e.model_desc,
        name="model-desc",
        methods=["POST"],
    ),
    path(
        "/model-detail",
        endpoint=e.model_detail,
        name="model-detail",
        methods=["POST"],
    ),
    path(
        "/model-action",
        endpoint=e.model_action,
        name="model-action",
        methods=["POST"],
    ),
    path(
        "/model-save",
        endpoint=e.model_save,
        name="model-save",
        methods=["POST"],
    ),
    path(
        "/model-delete",
        endpoint=e.model_delete,
        name="model-delete",
        methods=["POST"],
    ),
    path(
        "/model-data",
        endpoint=e.model_data,
        name="model-data",
        methods=["POST"],
    ),
]
