import typing as t

from unfazed.protocol import BaseLifeSpan

if t.TYPE_CHECKING:
    from unfazed.app import BaseAppConfig  # pragma: no cover
    from unfazed.core import Unfazed  # pragma: no cover


class AdminWakeup(BaseLifeSpan):
    def __init__(self, unfazed: Unfazed) -> None:
        self.unfazed = unfazed

    async def startup(self) -> None:
        # find all apps in unfazed.app_center
        # load all admin.py in each app

        app: "BaseAppConfig"
        for _, app in self.unfazed.app_center:
            app.wakeup("admin")

    async def shutdown(self) -> None:
        pass

    @property
    def state(self) -> t.Dict[str, t.Any]:
        return {}
