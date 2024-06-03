from pydantic import BaseModel

# from unfazed.conf.base import settings_from_key


class _Settings(BaseModel):
    pass


# settings = _Settings(**settings_from_key("TEST_APP_CONFIG"))