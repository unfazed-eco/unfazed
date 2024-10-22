import os

DEPLOY = os.getenv("DEPLOY", "dev")
PROJECT_NAME = os.getenv("PROJECT_NAME")

UNFAZED_SETTINGS = {
    "DEBUG": True if DEPLOY != "prod" else False,
    "DEPLOY": DEPLOY,
    "PROJECT_NAME": PROJECT_NAME,
    "ROOT_URLCONF": "entry.routes",
    "INSTALLED_APPS": [],
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "unfazed.db.tortoise.backends.mysql",
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
            "LOCATION": PROJECT_NAME,
        },
    },
    "MIDDLEWARE": ["unfazed.middleware.internal.errors.ServerErrorMiddleware"],
}
