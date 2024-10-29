from pydantic import BaseModel


class App1Settings(BaseModel):
    name: str = "app1"
