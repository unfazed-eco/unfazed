import os
import uuid

UNFAZED_SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_auth",
    "ROOT_URLCONF": "tests.test_contrib.test_auth.entry.routes",
    "INSTALLED_APPS": [
        "tests.apps.auth.common",
        "tests.apps.auth.deco",
        "unfazed.contrib.auth",
    ],
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.mysql",
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
    "MIDDLEWARE": [
        "unfazed.contrib.session.middleware.SessionMiddleware",
        "unfazed.contrib.auth.middleware.AuthenticationMiddleware",
    ],
}


UNFAZED_CONTRIB_AUTH_SETTINGS = {
    "CLIENT_CLASS": "unfazed.contrib.auth.settings.UnfazedContribAuthSettings",
    "USER_MODEL": "tests.apps.auth.common.models.User",
    "BACKENDS": {
        "default": {
            "BACKEND_CLS": "unfazed.contrib.auth.backends.default.DefaultAuthBackend",
            "OPTIONS": {},
        }
    },
}

SESSION_SETTINGS = {
    "CLIENT_CLASS": "unfazed.contrib.session.settings.SessionSettings",
    "SECRET": uuid.uuid4().hex,
    "COOKIE_DOMAIN": "http://testserver",
    "COOKIE_SECURE": True,
}
