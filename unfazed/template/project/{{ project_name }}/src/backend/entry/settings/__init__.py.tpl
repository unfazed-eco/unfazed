import os

DEPLOY = os.getenv("DEPLOY", "dev")
PROJECT_NAME = os.getenv("PROJECT_NAME", "{{project_name}}")
PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

LOG_DIR = os.path.join(PROJECT_DIR, "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "unfazed.log")

UNFAZED_SETTINGS = {
    "DEBUG": True if DEPLOY != "prod" else False,
    "DEPLOY": DEPLOY,
    "PROJECT_NAME": PROJECT_NAME,
    "ROOT_URLCONF": "entry.routes",
    "INSTALLED_APPS": [],
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.mysql",
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
    "MIDDLEWARE": ["unfazed.middleware.internal.common.CommonMiddleware"],
    "LOGGING": {
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "unfazed.logging.handlers.UnfazedRotatingFileHandler",
                "filename": LOG_FILE,
            },
        },
        "loggers": {
            "common": {
                "handlers": ["default"],
                "level": "INFO",
            },
        },
    },
}
