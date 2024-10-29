UNFAZED_SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "openapi",
    "ROOT_URLCONF": "tests.apps.openapi.backend.routes",
    "INSTALLED_APPS": ["common"],
    "MIDDLEWARE": ["unfazed.middleware.internal.errors.ServerErrorMiddleware"],
    "OPENAPI": {
        "servers": [{"url": "http://127.0.0.1:9527", "description": "Local"}],
    },
}
