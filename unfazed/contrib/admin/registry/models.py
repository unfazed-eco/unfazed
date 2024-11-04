import enum
import typing as t

from unfazed.db.tortoise.serializer import TSerializer
from unfazed.http import HttpRequest


class ModelType(enum.StrEnum):
    SITE = "site"
    DB = "db"
    CACHE = "cache"
    TOOL = "tool"


class BaseModel:
    model_type: str
    help_text: t.List[str] = []

    # route config
    component: str = ""
    icon: str = ""
    hidden: bool = False
    hidden_children: bool = False

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def title(self):
        return self.__class__.__name__

    def has_view_perm(self, request: HttpRequest, *args, **kw) -> bool:
        return True

    def has_change_perm(self, request: HttpRequest, *args, **kw) -> bool:
        return True

    def has_delete_perm(self, request: HttpRequest, *args, **kw) -> bool:
        return True

    def has_create_perm(self, request: HttpRequest, *args, **kw) -> bool:
        return True

    def to_serialize(self, *args, **kw) -> dict:
        raise NotImplementedError

    def get_actions(self) -> dict:
        pass

    def get_batch_actions(self) -> dict:
        pass

    def to_route(self) -> t.Dict[str, t.Any]:
        return {
            "title": self.title,
            "component": self.component,
            "name": self.name,
            "children": [],
            "meta": {
                "icon": self.icon,
                "hidden": self.hidden,
                "hideChildrenInMenu": self.hidden_children,
            },
        }


class SiteSettings(BaseModel):
    model_type = ModelType.SITE

    custom_settings: t.Dict[str, t.Any] = {}

    def to_serialize(self, *args, **kw) -> t.Dict[str, t.Any]:
        ret = {"title": self.title, "component": self.component}

        if self.custom_settings:
            ret.update(self.custom_settings)

        return ret


site = SiteSettings()


class ModelAdmin(BaseModel):
    _type = ModelType.DB
    serializer: TSerializer | None = None

    # fields description
    image_fields: t.List[str] = []
    datetime_fields: t.List[str] = []
    time_fields: t.List[str] = []
    editor_fields: t.List[str] = []
    readonly_fields: t.List[str] = []
    not_null_fields: t.List[str] = []
    json_fields: t.List[str] = []

    # behaviors on list page
    list_display: t.List[str] = []
    list_sort: t.List[str] = []
    list_filter: t.List[str] = []
    list_search: t.List[str] = []
    list_per_page: int = 20

    # behaviors on detail page
    detail_display: t.List[str] = []

    # default actions
    can_add: bool = True
    can_delete: bool = True
    can_edit: bool = True
    can_search: bool = True

    def get_actions(self) -> t.Dict[str, t.Dict]:
        pass

    def get_batch_actions(self) -> t.Dict[str, t.Dict]:
        pass

    def get_fields(self) -> t.Dict[str, t.Dict]:
        if not self.serializer:
            raise ValueError(f"serializer is not set for {self.__class__.__name__}")

    def get_attributes(self) -> t.Dict[str, t.Any]:
        pass


class ToolAdmin(BaseModel):
    pass


class CacheAdmin(BaseModel):
    pass
