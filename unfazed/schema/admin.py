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


class RouteMeta(BaseModel):
    icon: str | None = None
    hidden: bool = False
    hidden_children: bool = False


class AdminRoute(BaseModel):
    title: str
    component: str | None = None
    name: str
    icon: str | None = None
    children: list["AdminRoute"] = []
    meta: RouteMeta
