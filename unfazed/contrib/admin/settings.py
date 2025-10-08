import typing as t

from pydantic import BaseModel, Field

from unfazed.conf import register_settings


@register_settings("UNFAZED_CONTRIB_ADMIN_SETTINGS")
class UnfazedContribAdminSettings(BaseModel):
    defaultLoginType: bool = Field(
        default=True,
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
    title: str = Field(
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
