from pydantic import BaseModel, Field


class Condition(BaseModel):
    field: str = Field(description="field name")
    eq: float | int | str | None = Field(
        default=None,
        description="equal to this value",
        examples=["age__eq=18", "name__eq=admin"],
    )
    lt: float | int | None = Field(
        default=None, description="less than this value", examples=["age__lt=18"]
    )
    lte: float | int | None = Field(
        default=None,
        description="less than or equal to this value",
        examples=["age__lte=18"],
    )
    gt: float | int | None = Field(
        default=None, description="greater than this value", examples=["age__gt=18"]
    )
    gte: float | int | None = Field(
        default=None,
        description="greater than or equal to this value",
        examples=["age__gte=18"],
    )
    contains: str | None = Field(
        default=None,
        description="contains this value",
        examples=["name__contains=admin"],
    )
    icontains: str | None = Field(
        default=None,
        description="case insensitive contains this value",
        examples=["name__icontains=admin"],
    )


class AdminRoute(BaseModel):
    name: str = Field(description="name of this route")
    label: str = Field(description="label of this route")
    path: str = Field(description="path of this route")
    component: str | None = Field(default=None, description="component of this route")
    routes: list["AdminRoute"] = Field(
        default_factory=list, description="children routes of this route"
    )
    icon: str | None = Field(
        default=None,
        description="icon for this route from cdn",
        examples=[
            "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.7.2/svgs/solid/user.svg"
        ],
    )
    hideInMenu: bool = Field(
        default=False, description="hide this route in frontend admin"
    )
    hideChildrenInMenu: bool = Field(
        default=False, description="hide children routes in frontend admin"
    )
