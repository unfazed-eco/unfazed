import os

UNFAZED_SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_auth",
    "ROOT_URLCONF": "tests.test_contrib.test_auth.entry.routes",
    "INSTALLED_APPS": [
        "tests.apps.auth",
        "unfazed.contrib.auth",
    ],
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "unfazed.db.tortoise.backends.mysql",
                "CREDENTIALS": {
                    "HOST": os.environ.get("MYSQL_HOST", "mysql"),
                    "PORT": int(os.environ.get("MYSQL_PORT", 3306)),
                    "USER": "root",
                    "PASSWORD": "app",
                    "DATABASE": "test_app",
                },
            }
        }
    },
}


UNFAZED_CONTRIB_AUTH_SETTINGS = {
    "CLIENT_CLASS": "unfazed.contrib.auth.settings.UnfazedContribAuthSettings",
    "USER_MODEL": "tests.apps.auth.models.User",
    "BACKENDS": {
        "default": {
            "BACKEND_CLS": "unfazed.contrib.auth.backends.default.DefaultAuthBackend",
            "OPTIONS": {},
        }
    },
}
