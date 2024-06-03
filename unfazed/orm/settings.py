from pydantic import BaseModel


class BaseSettings(BaseModel):
    ENGINE: str
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    DATABASE: str
