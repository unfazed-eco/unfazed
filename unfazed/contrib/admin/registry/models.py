import enum
import typing as t

from pydantic.fields import FieldInfo

from unfazed.conf import UnfazedSettings, settings
from unfazed.db.tortoise.serializer import TSerializer
from unfazed.http import HttpRequest
from unfazed.protocol import BaseSerializer, CacheBackend
from unfazed.schema import AdminRoute

from .collector import admin_collector
from .decorators import action
from .fields import CharField, TextField
from .fields import Field as CustomField
from .schema import AdminAction, AdminAttrs, AdminField, AdminSerializeModel


class ModelType(enum.StrEnum):
    SITE = "site"
    DB = "db"
    CACHE = "cache"
    TOOL = "tool"


class BaseAdmin:
    model_type: str
    help_text: t.List[str] = []
    route_label: str = ""

    # route config
    component: str = ""
    icon: str = ""
    hidden: bool = False
    hidden_children: bool = False

    # register behavior
    override: bool = False

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def title(self):
        return self.__class__.__name__

    async def has_view_perm(self, request: HttpRequest, *args, **kw) -> bool:
        return request.user.is_superuser

    async def has_change_perm(self, request: HttpRequest, *args, **kw) -> bool:
        return request.user.is_superuser

    async def has_delete_perm(self, request: HttpRequest, *args, **kw) -> bool:
        return request.user.is_superuser

    async def has_create_perm(self, request: HttpRequest, *args, **kw) -> bool:
        return request.user.is_superuser

    async def has_action_perm(self, request: HttpRequest, *args, **kw) -> bool:
        return request.user.is_superuser

    def to_serialize(self, *args, **kw) -> dict:
        raise NotImplementedError

    def get_actions(self) -> t.Dict[str, AdminAction]:
        actions: t.Dict[str, AdminAction] = {}

        for ele in dir(self):
            if ele.startswith("__"):
                continue
            obj = getattr(self, ele)
            if hasattr(obj, "action"):
                attrs: AdminAction = obj.attrs
                actions[attrs.name] = attrs

        return actions

    def to_route(self) -> AdminRoute | None:
        return AdminRoute(
            title=self.title,
            component=self.component,
            name=self.name,
            children=[],
            meta={
                "icon": self.icon,
                "hidden": self.hidden,
                "hideChildrenInMenu": self.hidden_children,
            },
        )


class SiteSettings(BaseAdmin):
    navTheme: str = "light"
    colorPrimary: str = "#1890ff"
    layout: str = "mix"
    contentWidth: str = "Fluid"
    fixedHeader: bool = False
    fixSiderbar: bool = False
    colorWeak: bool = False
    title: str = "Unfazed Admin"
    pwa: bool = False
    logo: str = "https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg"
    iconfontUrl: str = ""
    pageSize: int = 20
    timeZone: str = "UTC"
    custom_settings: t.Dict[str, t.Any] = {}
    sitePrefix: str = "/admin"
    authType: t.List[int] = [1]

    def to_route(self) -> None:
        return None

    def to_serialize(self) -> t.Dict[str, t.Any]:
        unfazed_settings: UnfazedSettings = settings["UNFAZED_SETTINGS"]
        ret = {
            "title": self.title,
            "navTheme": self.navTheme,
            "colorPrimary": self.colorPrimary,
            "layout": self.layout,
            "contentWidth": self.contentWidth,
            "fixedHeader": self.fixedHeader,
            "colorWeak": self.colorWeak,
            "logo": self.logo,
            "pageSize": self.pageSize,
            "timeZone": self.timeZone,
            "sitePrefix": self.sitePrefix,
            "debug": unfazed_settings.DEBUG,
            "version": unfazed_settings.VERSION or "0.0.1",
            "authType": self.authType,
        }

        if self.custom_settings:
            ret.update(self.custom_settings)

        return ret


site = SiteSettings()


class BaseModelAdmin(BaseAdmin):
    serializer: t.Type[TSerializer]

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
    list_order: t.List[str] = []

    # default actions
    can_add: bool = True
    can_delete: bool = True
    can_edit: bool = True
    can_search: bool = True

    search_fields: t.List[str] = []

    def get_fields(self) -> t.Dict[str, t.Dict]:
        if not self.serializer:
            raise ValueError(f"serializer is not set for {self.__class__.__name__}")

        fields_mapping: t.Dict[str, t.Dict] = {}
        fields = self.serializer.model_fields
        fieldinfo: FieldInfo

        field_list = []
        not_null = []
        for name, fieldinfo in fields.items():
            field_class_name = fieldinfo.annotation.__name__

            field_list.append(name)
            if fieldinfo.default is None:
                not_null.append(name)

            json_schema_extra = getattr(fieldinfo, "json_schema_extra", {}) or {}
            choices = json_schema_extra.get("choices", [])

            fields_mapping[name] = AdminField(
                **{
                    "type": field_class_name,
                    "readonly": False,
                    "show": False,
                    "blank": True,
                    "choices": choices,
                    "help_text": fieldinfo.description,
                    "default": fieldinfo.get_default(),
                }
            )
        list_display = self.list_display or field_list
        for item in list_display:
            if item not in fields_mapping:
                raise ValueError(f"field '{item}' not included")
            fields_mapping[item].show = True

        readonly_fields = self.readonly_fields
        for item in readonly_fields:
            if item not in fields_mapping:
                raise ValueError(f"{item} should included in show_fields")
            fields_mapping[item].readonly = True

        image_fields = self.image_fields
        for item in image_fields:
            if item in fields_mapping:
                fields_mapping[item].field_type = "ImageField"

        datetime_fields = self.datetime_fields
        for item in datetime_fields:
            if item in fields_mapping:
                fields_mapping[item].field_type = "DatetimeField"

        time_fields = self.time_fields
        for item in time_fields:
            if fields_mapping[item].field_type != "TimeField":
                raise ValueError(f"{item} should be TimeField")

        editor_fields = self.editor_fields
        for item in editor_fields:
            if item in fields_mapping:
                fields_mapping[item].field_type = "EditorField"

        json_fields = self.json_fields
        for item in json_fields:
            if item in fields_mapping:
                fields_mapping[item].field_type = "JsonField"

        not_null_fields = self.not_null_fields + not_null or list_display
        for item in not_null_fields:
            if item not in fields_mapping:
                raise ValueError(f"{item} show include in show_fields")
            fields_mapping[item].blank = False

        return fields_mapping


class ModelAdmin(BaseModelAdmin):
    can_show_all: bool = True

    # behaviors on detail page
    detail_display: t.List[str] = []

    # have edit btn to detail page
    editable: bool = True

    # relations
    inlines: t.List[BaseModelAdmin | str] = []

    def to_inlines(self) -> t.Dict:
        inlines = self.inlines
        if not inlines:
            return {}

        ret = {}
        self_serializer: BaseSerializer = self.serializer
        for inline in inlines:
            if isinstance(inline, str):
                inline = admin_collector[inline]

            inline_serializer: BaseSerializer = inline.serializer
            relation = inline_serializer.find_relation(self_serializer)

            if not relation:
                raise ValueError(
                    f"dont have relation between {inline.name} and {self.name} not found"
                )

            elif relation.relation == "bk_fk":
                raise ValueError(
                    f"bk_fk relation between {inline.name} and {self.name} is not supported"
                )

            elif relation.relation == "bk_o2o":
                raise ValueError(
                    f"bk_o2o relation between {inline.name} and {self.name} is not supported"
                )

            else:
                ret[inline.name] = relation.model_dump()

        return ret

    def to_serialize(self, *args, **kw) -> AdminSerializeModel:
        fields_map = self.get_fields()
        actions = self.get_actions()

        detail_display = self.detail_display or [
            name for name in self.serializer.Meta.model._meta.db_fields
        ]
        attrs = {
            "editable": self.editable,
            "help_text": self.help_text,
            "can_show_all": self.can_show_all,
            "can_search": self.can_search,
            "search_fields": self.search_fields or detail_display,
            "list_per_page": self.list_per_page,
            "detail_display": detail_display,
            "can_add": self.can_add,
            "list_search": self.list_search,
            "can_delete": self.can_delete,
            "can_edit": self.can_edit,
        }

        list_filter = self.list_filter
        for item in list_filter:
            if item not in fields_map:
                raise ValueError(f"{item} not found in show_fields")
        attrs["list_filter"] = list_filter

        list_sort = self.list_sort
        for item in list_sort:
            if item not in fields_map:
                raise ValueError(f"{item} not found in show_fields")
        attrs["list_sort"] = list_sort

        return AdminSerializeModel(
            fields=fields_map,
            actions=actions,
            attrs=AdminAttrs(**attrs),
        )


class ModelInlineAdmin(ModelAdmin):
    # behaviors on list page
    list_show_type: int
    max_num: int = 0
    min_num: int = 0

    # item control
    can_copy: bool = False

    def to_route(self) -> None:
        return None

    def to_serialize(self) -> dict:
        fields_map = self.get_fields()

        attrs = {
            "help_text": self.help_text,
            "list_show_type": self.list_show_type,
            "max_num": self.max_num,
            "min_num": self.min_num,
            "can_copy": self.can_copy,
            "can_add": self.can_add,
            "can_delete": self.can_delete,
            "can_edit": self.can_edit,
            "can_search": self.can_search,
            "list_per_page": self.list_per_page,
            "list_order": self.list_order,
            "list_search": self.list_search,
        }

        list_filter = self.list_filter
        for item in list_filter:
            if item not in fields_map:
                raise ValueError(f"{item} not found in show_fields")
        attrs["list_filter"] = list_filter

        list_sort = self.list_sort
        for item in list_sort:
            if item not in fields_map:
                raise ValueError(f"{item} not found in show_fields")
        attrs["list_sort"] = list_sort

        return {
            "fields": fields_map,
            "attrs": attrs,
            "actions": self.get_actions(),
        }


class ToolAdmin(BaseAdmin):
    fields_set: t.List[CustomField] = []
    route_label: str = "Tools"
    output_field: str

    def to_serialize(self) -> dict:
        fields_map = {}
        for field in self.fields_set:
            fields_map[field.name] = field.to_json()

        attrs = {
            "output_field": self.output_field,
            "help_text": self.help_text,
        }

        actions = self.get_actions()

        return {
            "fields": fields_map,
            "actions": actions,
            "attrs": attrs,
        }


class CacheAdmin(BaseAdmin):
    route_label: str = "Cache"
    fields_set: t.List[CustomField] = [
        CharField(name="key", help_text="cache key"),
        TextField(name="value", help_text="cache value"),
    ]

    output_field: str = "value"

    cache_client: CacheBackend

    @action(name="search")
    async def search(self, key: str, *args, **kw) -> t.Any:
        return await self.cache_client.get(key)

    @action(name="set")
    async def set(self, key: str, value: t.Any, *args, **kw) -> t.Any:
        return await self.cache_client.set(key, value)

    @action(name="delete")
    async def delete(self, key: str, *args, **kw) -> t.Any:
        return await self.cache_client.delete(key)
