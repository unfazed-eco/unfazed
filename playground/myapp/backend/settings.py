UNFAZED_SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "myapp",
    "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
    "ROOT_URLCONF": "playground.myapp.backend.routes",
    "INSTALLED_APPS": ["account", "student"],
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "unfazed.orm.tortoise.backends.mysql",
                "CREDENTIALS": {
                    "HOST": "mysql",
                    "PORT": 3306,
                    "USER": "root",
                    "PASSWORD": "app",
                    "DATABASE": "app",
                },
            }
        }
    },
    "CACHE": {
        "default": {
            "BACKEND": "unfazed.cache.backends.locmem.LocMemCache",
            "LOCATION": "playground.myapp",
        },
    },
    "MIDDLEWARE": ["unfazed.middleware.internal.errors.ServerErrorMiddleware"],
    "OPENAPI": {
        "servers": ["http://127.0.0.1:9527"],
    },
}
