UNFAZED_SETTINGS = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_launch",
    "CLIENT_CLASS": "unfazed.conf.UnfazedSettings",
    "ROOT_URLCONF": "tests.apps.orm.routes",
    "INSTALLED_APPS": ["tests.apps.orm.common"],
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
}

