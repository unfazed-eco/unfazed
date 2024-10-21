from unfazed.conf import settings
from pydantic import BaseModel



class {{ app_name | capitalize }}Settings(BaseModel):
    pass



{{ app_name }}_settings = settings["{{ app_name | capitalize }}_Settings"]

