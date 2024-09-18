from unfazed.route import path

from .endpoints import openapi_json, redoc

patterns = [
    path("/redoc", endpoint=redoc, ignore=True),
    path("/openapi.json", endpoint=openapi_json, ignore=True),
]
