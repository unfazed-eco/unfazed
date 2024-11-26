import os

UNFAZED_SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_admin",
    "ROOT_URLCONF": "tests.test_contrib.test_admin.entry.routes",
    "INSTALLED_APPS": [
        "tests.apps.admin.account",
        "tests.apps.admin.article",
        "unfazed.contrib.admin",
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
