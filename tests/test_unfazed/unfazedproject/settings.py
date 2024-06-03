INSTALLED_APPS = ["unfazedproject.app"]
MIDDLEWARE = ["unfazedproject.middlewares.m1.CustomMiddleware1"]
DEBUG: bool = True
ROOT_URLCONF: str = "unfazedproject.routes"
PROJECT_NAME: str = "unfazedproject"
