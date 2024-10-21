from unfazed.route import path

from .endpoints import docs, openapi_json, redoc

patterns = [
    path("/openapi/redoc", endpoint=redoc, include_in_schema=False),
    path("/openapi/docs", endpoint=docs, include_in_schema=False),
    path("/openapi/openapi.json", endpoint=openapi_json, include_in_schema=False),
]
