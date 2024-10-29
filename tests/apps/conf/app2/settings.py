from pydantic import BaseModel


class App2Settings(BaseModel):
    name: str = "app2"
