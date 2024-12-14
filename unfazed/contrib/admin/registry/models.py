import inspect
import typing as t
from enum import Enum
from itertools import chain

from pydantic.fields import FieldInfo
from tortoise import Model as TModel

from unfazed.conf import UnfazedSettings, settings
from unfazed.http import HttpRequest
from unfazed.schema import AdminRoute, RouteMeta
from unfazed.serializer import Serializer

from .collector import admin_collector
from .decorators import action
from .fields import CharField, TextField
from .fields import Field as CustomField
from .schema import (
    AdminAction,
    AdminAttrs,
    AdminField,
    AdminInlineAttrs,
    AdminInlineSerializeModel,
    AdminSerializeModel,
    AdminSite,
    AdminToolAttrs,
    AdminToolSerializeModel,
)
from .utils import convert_field_type

if t.TYPE_CHECKING:
    from unfazed.cache.backends.locmem import LocMemCache  # pragma: no cover
    from unfazed.cache.backends.redis.serializedclient import (
        SerializerBackend,  # pragma: no cover
    )


class BaseAdmin:
    help_text: t.List[str] = []
    route_label: str | None = None

    # route config
    component: str = ""
    icon: str = ""
    hidden: bool = False
    hidden_children: bool = False

    # register behavior
    override: bool = False

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def title(self) -> str:
        return self.__class__.__name__

    async def has_view_perm(
        self, request: HttpRequest, *args: t.Any, **kw: t.Any
    ) -> bool:
        return request.user.is_superuser == 1

    async def has_change_perm(
        self, request: HttpRequest, *args: t.Any, **kw: t.Any
    ) -> bool:
        return request.user.is_superuser == 1

    async def has_delete_perm(
        self, request: HttpRequest, *args: t.Any, **kw: t.Any
    ) -> bool:
        return request.user.is_superuser == 1

    async def has_create_perm(
        self, request: HttpRequest, *args: t.Any, **kw: t.Any
    ) -> bool:
        return request.user.is_superuser == 1

    async def has_action_perm(
        self, request: HttpRequest, *args: t.Any, **kw: t.Any
    ) -> bool:
        return request.user.is_superuser == 1

    def to_serialize(
        self,
    ) -> t.Union[
        AdminSite,
        AdminSerializeModel,
        AdminInlineSerializeModel,
        AdminToolSerializeModel,
    ]:
        raise NotImplementedError  # pragma: no cover

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
            meta=RouteMeta(
                icon=self.icon,
                hidden=self.hidden,
                hidden_children=self.hidden_children,
            ),
        )


class SiteSettings(BaseAdmin):
    # antd properties
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

    # antd will call backend api use this prefix
    # for example, if apiPrefix is /api/contrib/admin
    # antd will call /api/contrib/admin/model-data to get data
    apiPrefix: str = "/api/contrib/admin"

    # auth type
    # TODO
    authPlugins: t.List[t.Dict[str, t.Any]] = []

    # custom settings
    # If the frontend is integrated with other non-unfazed-admin,
    # additional configurations can be passed through this field
    extra: t.Dict[str, t.Any] = {}

    def to_route(self) -> None:
        return

    def to_serialize(self) -> AdminSite:
        unfazed_settings: UnfazedSettings = settings["UNFAZED_SETTINGS"]
        ret = AdminSite.model_validate(
            {
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
                "apiPrefix": self.apiPrefix,
                "debug": unfazed_settings.DEBUG,
                "version": unfazed_settings.VERSION or "0.0.1",
                "authPlugins": self.authPlugins,
                "extra": self.extra,
            }
        )

        return ret


site = SiteSettings()


class BaseModelAdmin(BaseAdmin):
    serializer: t.Type[Serializer]

    # fields description
    image_fields: t.List[str] = []
    datetime_fields: t.List[str] = []
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

    # search panel
    can_search: bool = True
    search_fields: t.List[str] = []

    def get_fields(self) -> t.Dict[str, AdminField]:
        if not hasattr(self, "serializer"):
            raise ValueError(f"serializer is not set for {self.__class__.__name__}")

        fields_mapping: t.Dict[str, AdminField] = {}
        fields = self.serializer.model_fields
        fieldinfo: FieldInfo

        field_list = []
        not_null = []
        for name, fieldinfo in fields.items():
            field_list.append(name)
            if fieldinfo.default is None:
                not_null.append(name)

            json_schema_extra = getattr(fieldinfo, "json_schema_extra", {}) or {}

            raw_field_type = json_schema_extra.get("field_type", None)
            if not raw_field_type:
                raw_field_type = (
                    fieldinfo.annotation.__name__ if fieldinfo.annotation else ""
                )

            field_type = convert_field_type(raw_field_type)

            if inspect.isclass(fieldinfo.annotation) and issubclass(
                fieldinfo.annotation, Enum
            ):
                choices = [(item.name, item.value) for item in fieldinfo.annotation]
            else:
                choices = json_schema_extra.get("choices", None) or []

            fields_mapping[name] = AdminField.model_validate(
                {
                    "type": field_type,
                    "readonly": False,
                    "show": False,
                    "blank": True,
                    "choices": choices,
                    "help_text": fieldinfo.description or "",
                    "default": fieldinfo.get_default(call_default_factory=True),
                }
            )
        list_display = self.list_display or field_list
        not_null_fields = self.not_null_fields + not_null

        for item in chain(
            list_display,
            self.readonly_fields,
            self.image_fields,
            self.datetime_fields,
            self.editor_fields,
            self.json_fields,
            not_null_fields,
        ):
            if item not in fields_mapping:
                raise ValueError(f"field '{item}' not included in {field_list}")
        for item in list_display:
            fields_mapping[item].show = True

        readonly_fields = self.readonly_fields
        for item in readonly_fields:
            fields_mapping[item].readonly = True

        image_fields = self.image_fields
        for item in image_fields:
            fields_mapping[item].field_type = "ImageField"

        datetime_fields = self.datetime_fields
        for item in datetime_fields:
            if fields_mapping[item].field_type not in [
                "DatetimeField",
                "DateField",
                "IntegerField",
                "FloatField",
            ]:
                raise ValueError(
                    f"{item} should be DatetimeField or DateField or IntegerField or FloatField"
                )
            fields_mapping[item].field_type = "DatetimeField"

        editor_fields = self.editor_fields
        for item in editor_fields:
            fields_mapping[item].field_type = "EditorField"

        json_fields = self.json_fields
        for item in json_fields:
            fields_mapping[item].field_type = "JsonField"

        for item in not_null_fields:
            fields_mapping[item].blank = False

        return fields_mapping


class ModelAdmin(BaseModelAdmin):
    # behaviors on list page
    can_show_all: bool = False

    # behaviors on detail page
    detail_display: t.List[str] = []

    # have edit btn to detail page
    editable: bool = True

    # relations
    inlines: t.List[str] = []

    def to_inlines(self) -> t.Dict:
        inlines = self.inlines
        if not inlines:
            return {}

        ret = {}
        self_serializer: t.Type[Serializer] = self.serializer
        for name in inlines:
            inline = admin_collector[name]

            inline_serializer: Serializer = inline.serializer
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

    def get_attrs(self, field_list: t.List[str]) -> AdminAttrs:
        model: t.Type[TModel] = self.serializer.Meta.model
        detail_display = self.detail_display or list(model._meta.db_fields)
        for item in chain(
            detail_display,
            self.list_filter,
            self.list_sort,
            self.list_order,
            self.search_fields,
        ):
            if item not in field_list:
                raise ValueError(f"field {item} not found in {field_list}")

        attrs = AdminAttrs.model_validate(
            {
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
                "list_filter": self.list_filter,
                "list_sort": self.list_sort,
                "list_order": self.list_order,
            }
        )

        return attrs

    def to_serialize(self) -> AdminSerializeModel:
        fields_map = self.get_fields()
        actions = self.get_actions()
        attrs = self.get_attrs(list(fields_map.keys()))

        return AdminSerializeModel(
            fields=fields_map,
            actions=actions,
            attrs=attrs,
        )


class ModelInlineAdmin(ModelAdmin):
    # behaviors on list page

    max_num: int = 0
    min_num: int = 0

    # item control
    can_copy: bool = False

    def to_route(self) -> None:
        return None

    @t.override
    def get_attrs(self, field_list: t.List[str]) -> AdminInlineAttrs:  # type: ignore
        model: t.Type[TModel] = self.serializer.Meta.model
        list_display = self.list_display or list(model._meta.db_fields)

        for item in chain(
            list_display,
            self.list_filter,
            self.list_sort,
            self.list_order,
            self.search_fields,
        ):
            if item not in field_list:
                raise ValueError(f"field {item} not found in {field_list}")

        attrs = AdminInlineAttrs.model_validate(
            {
                "help_text": self.help_text,
                "max_num": self.max_num,
                "min_num": self.min_num,
                "can_copy": self.can_copy,
                "can_show_all": self.can_show_all,
                "can_search": self.can_search,
                "search_fields": self.search_fields or list_display,
                "list_per_page": self.list_per_page,
                "can_add": self.can_add,
                "list_search": self.list_search,
                "can_delete": self.can_delete,
                "can_edit": self.can_edit,
                "list_filter": self.list_filter,
                "list_sort": self.list_sort,
                "list_order": self.list_order,
            }
        )

        return attrs

    @t.override
    def to_serialize(self) -> AdminInlineSerializeModel:  # type: ignore
        fields_map = self.get_fields()
        attrs = self.get_attrs(list(fields_map.keys()))

        return AdminInlineSerializeModel(
            fields=fields_map, attrs=attrs, actions=self.get_actions()
        )


class ToolAdmin(BaseAdmin):
    fields_set: t.List[CustomField] = []
    route_label: str = "Tools"
    output_field: str

    @t.override
    def to_serialize(self) -> AdminToolSerializeModel:
        fields_map = {}
        for field in self.fields_set:
            fields_map[field.name] = field.to_json()

        attrs = AdminToolAttrs(output_field=self.output_field, help_text=self.help_text)

        actions = self.get_actions()

        return AdminToolSerializeModel(
            fields=fields_map,
            actions=actions,
            attrs=attrs,
        )


class CacheAdmin(BaseAdmin):
    route_label: str = "Cache"
    fields_set: t.List[CustomField] = [
        CharField(name="key", help_text="cache key"),
        TextField(name="value", help_text="cache value"),
    ]

    output_field: str = "value"

    cache_client: t.Union["LocMemCache", "SerializerBackend"]

    @action(name="search")
    async def search(self, data: t.Dict, request: HttpRequest | None = None) -> t.Any:
        key = data.get("key", None)
        return await self.cache_client.get(key)

    @action(name="set")
    async def set(self, data: t.Dict, request: HttpRequest | None = None) -> t.Any:
        key = data.get("key", None)
        value = data.get("value", None)

        return await self.cache_client.set(key, value)

    @action(name="delete")
    async def delete(self, data: t.Dict, request: HttpRequest | None = None) -> t.Any:
        key = data.get("key", None)

        return await self.cache_client.delete(key)
