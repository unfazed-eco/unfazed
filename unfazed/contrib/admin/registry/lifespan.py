import typing as t

from unfazed.lifespan import BaseLifeSpan

if t.TYPE_CHECKING:
    from unfazed.app import BaseAppConfig  # pragma: no cover


class AdminWakeup(BaseLifeSpan):
    async def on_startup(self) -> None:
        # find all apps in unfazed.app_center
        # load all admin.py in each app

        app: "BaseAppConfig"
        for _, app in self.unfazed.app_center:
            app.wakeup("admin")
