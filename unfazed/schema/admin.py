from pydantic import BaseModel


class Condtion(BaseModel):
    field: str
    eq: float | int | str | None = None
    lt: float | int | None = None
    lte: float | int | None = None
    gt: float | int | None = None
    gte: float | int | None = None
    contains: str | None = None
    icontains: str | None = None


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
