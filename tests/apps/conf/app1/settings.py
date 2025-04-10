from pydantic import BaseModel

from unfazed.conf import register_settings


@register_settings("APP1_SETTINGS")
class App1Settings(BaseModel):
    name: str = "app1"
