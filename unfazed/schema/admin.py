from pydantic import BaseModel, Field
import typing as t


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
        description="icon for this route from ant design",
        examples=[
            "table",
            "user",
            "setting",
            "home",
            "dashboard",
            "file",
            "folder",
        ],
    )
    hideInMenu: bool = Field(
        default=False, description="hide this route in frontend admin"
    )
    hideChildrenInMenu: bool = Field(
        default=False, description="hide children routes in frontend admin"
    )


class AdminOptions(BaseModel):
    defaultLoginType: bool = Field(
        default=False,
        alias="DEFAULT_LOGIN_TYPE",
        description="default login type of this admin site",
    )
    authPlugins: t.List[t.Dict[str, t.Any]] = Field(
        default=[
            {
                "icon_url": "https://developers.google.com/identity/images/g-logo.png",
                "platform": "google",
            },
        ],
        alias="AUTH_PLUGINS",
        description="auth plugins of this admin site, see https://ant.design/components/app-api-reference/components/app#authPlugins",
    )
    title: t.Dict[str, t.Any] = Field(
        default="Unfazed Admin",
        alias="TITLE",
        description="title of this admin site",
    )
    extra: t.Dict[str, t.Any] = Field(
        default={},
        alias="EXTRA",
        description="extra data for this admin site",
    )
    logo: str = Field(
        default="https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg",
        alias="LOGO",
        description="logo of this admin site",
    )
    iconfontUrl: str = Field(
        default="",
        alias="ICONFONT_URL",
        description="iconfont url of this admin site",
    )
    showWatermark: bool = Field(
        default=True,
        alias="SHOW_WATERMARK",
        description="show watermark of this admin site",
    )
    timeZone: str = Field(
        default="UTC",
        alias="TIME_ZONE",
        description="time zone of this admin site",
    )
    apiPrefix: str = Field(
        default="/api/contrib/admin",
        alias="API_PREFIX",
        description="api prefix of this admin site",
    )
    websitePrefix: str = Field(
        default="/admin",
        alias="WEBSITE_PREFIX",
        description="website prefix of this admin site",
    )
