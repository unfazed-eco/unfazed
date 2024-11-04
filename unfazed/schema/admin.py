from pydantic import BaseModel


class Condtion(BaseModel):
    field: str
    eq: float | int | str | None
    lt: float | int | None
    lte: float | int | None
    gt: float | int | None
    gte: float | int | None
    contains: str | None
    icontains: str | None
