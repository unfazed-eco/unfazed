import inspect
import typing as t
from enum import Enum
from functools import cached_property
from itertools import chain

from pydantic.fields import FieldInfo
from tortoise import Model as TModel

from unfazed.conf import UnfazedSettings, settings
from unfazed.contrib.admin.settings import UnfazedContribAdminSettings
from unfazed.http import HttpRequest
from unfazed.protocol import AdminAuthProtocol
from unfazed.schema import AdminRoute
from unfazed.serializer import Serializer

from .collector import admin_collector
from .fields import Field as CustomField
from .schema import (
    AdminAction,
    AdminAttrs,
    AdminCustomAttrs,
    AdminCustomSerializeModel,
    AdminField,
    AdminInlineAttrs,
    AdminInlineSerializeModel,
    AdminRelation,
    AdminSerializeModel,
    AdminSite,
    AutoFill,
)
from .utils import convert_field_type, smart_split


class BaseAdmin:
    help_text: str = ""

    # route config
    component: str = "ModelAdmin"
    icon: str = ""
    hideInMenu: bool = False
    hideChildrenInMenu: bool = False

    # register behavior
    override: bool = False

    _label: str | None = None

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def path(self) -> str:
        return f"/{self.name}"

    @property
    def label(self) -> str:
        if self._label:
            return self._label
        return smart_split(self.name)

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
        AdminCustomSerializeModel,
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
            component=self.component,
            path=self.path,
            name=self.name,
            label=self.label,
            routes=[],
            icon=self.icon,
            hideInMenu=self.hideInMenu,
            hideChildrenInMenu=self.hideChildrenInMenu,
        )


class SiteSettings(BaseAdmin):
    # antd properties
    navTheme: str = "light"
    colorPrimary: str = "#1890ff"
    layout: str = "mix"
    contentWidth: str = "Fluid"
    fixedHeader: bool = False
    fixSiderbar: bool = True
    colorWeak: bool = False
    title: str = "Unfazed Admin"
    pwa: bool = False
    logo: str = "https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg"
    iconfontUrl: str = ""
    pageSize: int = 20
    timeZone: str = "UTC"
    showWatermark: bool = True
    defaultLoginType: bool = False
    websitePrefix: str = "/admin"

    # antd will call backend api use this prefix
    # for example, if apiPrefix is /api/contrib/admin
    # antd will call /api/contrib/admin/model-data to get data
    apiPrefix: str = "/api/contrib/admin"

    # auth type
    # TODO
    authPlugins: t.List[t.Dict[str, t.Any]] = [
        {
            "icon_url": "https://developers.google.com/identity/images/g-logo.png",
            "platform": "google",
        },
    ]

    # custom settings
    # If the frontend is integrated with other non-unfazed-admin,
    # additional configurations can be passed through this field
    extra: t.Dict[str, t.Any] = {}

    def to_route(self) -> None:
        return

    def to_serialize(self) -> AdminSite:
        unfazed_contrib_admin_settings: UnfazedContribAdminSettings = settings[
            "UNFAZED_CONTRIB_ADMIN_SETTINGS"
        ]

        unfazed_settings: UnfazedSettings = settings["UNFAZED_SETTINGS"]

        ret = AdminSite.model_validate(
            {
                "title": (
                    unfazed_contrib_admin_settings.title
                    if unfazed_contrib_admin_settings
                    else self.title
                ),
                "navTheme": self.navTheme,
                "colorPrimary": self.colorPrimary,
                "layout": self.layout,
                "contentWidth": self.contentWidth,
                "fixedHeader": self.fixedHeader,
                "fixSiderbar": self.fixSiderbar,
                "colorWeak": self.colorWeak,
                "pwa": self.pwa,
                "logo": (
                    unfazed_contrib_admin_settings.logo
                    if unfazed_contrib_admin_settings
                    else self.logo
                ),
                "pageSize": self.pageSize,
                "timeZone": (
                    unfazed_contrib_admin_settings.timeZone
                    if unfazed_contrib_admin_settings
                    else self.timeZone
                ),
                "apiPrefix": (
                    unfazed_contrib_admin_settings.apiPrefix
                    if unfazed_contrib_admin_settings
                    else self.apiPrefix
                ),
                "debug": unfazed_settings.DEBUG,
                "version": unfazed_settings.VERSION or "0.0.1",
                "authPlugins": (
                    unfazed_contrib_admin_settings.authPlugins
                    if unfazed_contrib_admin_settings.authPlugins
                    else self.authPlugins
                ),
                "extra": (
                    unfazed_contrib_admin_settings.extra
                    if unfazed_contrib_admin_settings
                    else self.extra
                ),
                "iconfontUrl": (
                    unfazed_contrib_admin_settings.iconfontUrl
                    if unfazed_contrib_admin_settings
                    else self.iconfontUrl
                ),
                "showWatermark": (
                    unfazed_contrib_admin_settings.showWatermark
                    if unfazed_contrib_admin_settings
                    else self.showWatermark
                ),
                "defaultLoginType": (
                    unfazed_contrib_admin_settings.defaultLoginType
                    if unfazed_contrib_admin_settings
                    else self.defaultLoginType
                ),
                "websitePrefix": (
                    unfazed_contrib_admin_settings.websitePrefix
                    if unfazed_contrib_admin_settings
                    else self.websitePrefix
                ),
            }
        )

        return ret


site = SiteSettings()


class BaseModelAdmin(BaseAdmin, AdminAuthProtocol):
    serializer: t.Type[Serializer]

    # fields description
    image_fields: t.List[str] = []
    datetime_fields: t.List[str] = []
    editor_fields: t.List[str] = []
    readonly_fields: t.List[str] = []
    not_null_fields: t.List[str] = []
    json_fields: t.List[str] = []

    # behaviors on list page

    # decide which fields to display
    list_display: t.List[str] = []

    # sort by fields -> click on the column header
    list_sort: t.List[str] = []

    # filter by fields
    list_filter: t.List[str] = []

    # search by fields
    list_search: t.List[str] = []

    # range search fields(must be in list_search)
    list_range_search: t.List[str] = []

    # default number of items to display per page
    list_per_page: int = 20

    # options for number of items to display per page
    list_per_page_options: t.List[int] = [10, 20, 50, 100]

    # order by fields -> display order of the items
    list_order: t.List[str] = []

    # can edit the items in the list page
    list_editable: t.List[str] = []

    # will show a Add button in frontend admin if can_add is True
    can_add: bool = True
    # will show a Delete button in frontend admin if can_delete is True
    can_delete: bool = True
    # the data can be edited inlines
    can_edit: bool = True

    # route label
    _route_label: str | None = "Model"

    @property
    def route_label(self) -> str:
        if self.app_label:
            return self.app_label
        return self._route_label or ""

    @cached_property
    def model_description(self) -> t.Dict[str, t.Any]:
        model: t.Type[TModel] = self.serializer.Meta.model  # type: ignore
        return model.describe()

    @property
    def permission_prefix(self) -> str:
        return f"{self.model_description['app']}.{self.model_description['table']}"

    @property
    def view_permission(self) -> str:
        return f"{self.permission_prefix}.can_view"

    @property
    def change_permission(self) -> str:
        return f"{self.permission_prefix}.can_change"

    @property
    def delete_permission(self) -> str:
        return f"{self.permission_prefix}.can_delete"

    @property
    def create_permission(self) -> str:
        return f"{self.permission_prefix}.can_create"

    def action_permission(self, action: str) -> str:
        return f"{self.permission_prefix}.can_exec_{action}"

    def get_all_permissions(self) -> t.List[str]:
        return [
            self.view_permission,
            self.change_permission,
            self.delete_permission,
            self.create_permission,
        ] + [self.action_permission(action) for action in self.get_actions()]  # type: ignore

    @property
    def app_label(self) -> str:
        serializer_path: str = self.serializer.Meta.__module__
        unfazed_settings: UnfazedSettings = settings["UNFAZED_SETTINGS"]
        for app_full_name in unfazed_settings.INSTALLED_APPS:
            if serializer_path.startswith(app_full_name):
                return app_full_name.split(".")[-1]
        return ""

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
                choices = [(item.value, item.name) for item in fieldinfo.annotation]
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
                    "name": name,
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

    # behaviors on detail page
    # decide which fields to display
    detail_display: t.List[str] = []
    # order by fields -> display order of the items in detail page
    detail_order: t.List[str] = []
    # decide which fields can be edited
    detail_editable: t.List[str] = []

    # relations
    # currently unfazed need developers define the relation clearly
    inlines: t.List[AdminRelation] = []

    def to_inlines(self) -> t.Dict[str, AdminInlineSerializeModel]:
        inlines = self.inlines
        if not inlines:
            return {}

        ret = {}
        self_serializer: t.Type[Serializer] = self.serializer
        for admin_relation in inlines:
            name = admin_relation.target
            inline: ModelInlineAdmin = admin_collector[name]

            if not isinstance(inline, ModelInlineAdmin):
                raise ValueError(
                    f"inline {inline.name} is not a ModelInlineAdmin, it is a {type(inline)}"
                )

            inline_serializer: t.Type[Serializer] = inline.serializer
            relation = self_serializer.find_relation(inline_serializer)

            if isinstance(admin_relation.relation, AutoFill):
                if not relation:
                    raise ValueError(
                        f"dont have relation between {inline.name} and {self.name}"
                    )

                else:
                    admin_relation.relation = relation.relation

                if (
                    isinstance(admin_relation.source_field, AutoFill)
                    and relation.source_field is not None
                ):
                    admin_relation.source_field = relation.source_field

                if (
                    isinstance(admin_relation.target_field, AutoFill)
                    and relation.target_field is not None
                ):
                    admin_relation.target_field = relation.target_field

            # check if the fields are correctly defined
            if admin_relation.relation == "m2m":
                assert admin_relation.through is not None
                mid_name = admin_relation.through.through
                mid_admin: ModelInlineAdmin = admin_collector[mid_name]
                mid_serializer: t.Type[Serializer] = mid_admin.serializer

                mid_fields = mid_serializer.model_fields

                if admin_relation.through.target_to_through_field not in mid_fields:
                    raise ValueError(
                        f"field {admin_relation.through.target_to_through_field} not found in {mid_fields}"
                    )

                if admin_relation.through.source_to_through_field not in mid_fields:
                    raise ValueError(
                        f"field {admin_relation.through.source_to_through_field} not found in {mid_fields}"
                    )

                if (
                    admin_relation.through.source_field
                    not in self_serializer.model_fields
                ):
                    raise ValueError(
                        f"field {admin_relation.through.source_field} not found in {self_serializer.model_fields}"
                    )

                if (
                    admin_relation.through.target_field
                    not in inline_serializer.model_fields
                ):
                    raise ValueError(
                        f"field {admin_relation.through.target_field} not found in {inline_serializer.model_fields}"
                    )

            else:
                if admin_relation.source_field not in self_serializer.model_fields:
                    raise ValueError(
                        f"field {admin_relation.source_field} not found in {self_serializer.model_fields}"
                    )

                if admin_relation.target_field not in inline_serializer.model_fields:
                    raise ValueError(
                        f"field {admin_relation.target_field} not found in {inline_serializer.model_fields}"
                    )

            admin_inline_serialize_model: AdminInlineSerializeModel = (
                inline.to_serialize()
            )
            admin_inline_serialize_model.relation = admin_relation
            ret[inline.name] = admin_inline_serialize_model

        return ret

    def get_attrs(self, field_list: t.List[str]) -> AdminAttrs:
        model: t.Type[TModel] = self.serializer.Meta.model
        detail_display = self.detail_display or list(model._meta.db_fields)
        for item in chain(
            self.list_filter,
            self.list_sort,
            self.list_order,
            self.list_search,
            self.list_range_search,
            self.list_editable,
            detail_display,
            self.detail_order,
            self.detail_editable,
        ):
            if item not in field_list:
                raise ValueError(f"field {item} not found in {field_list}")

        attrs = AdminAttrs.model_validate(
            {
                "help_text": self.help_text,
                "list_editable": self.list_editable,
                "list_filter": self.list_filter,
                "list_sort": self.list_sort,
                "list_order": self.list_order,
                "list_search": self.list_search,
                "list_range_search": self.list_range_search,
                "list_per_page": self.list_per_page,
                "list_per_page_options": self.list_per_page_options,
                "can_add": self.can_add,
                "can_delete": self.can_delete,
                "can_edit": self.can_edit,
                "detail_display": detail_display,
                "detail_order": self.detail_order,
                "detail_editable": self.detail_editable,
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

    def to_route(self) -> None:
        return None

    @t.override
    def get_attrs(self, field_list: t.List[str]) -> AdminInlineAttrs:  # type: ignore
        model: t.Type[TModel] = self.serializer.Meta.model
        list_display = self.list_display or list(model._meta.db_fields)

        for item in chain(
            list_display,
            self.list_sort,
            self.list_filter,
            self.list_order,
            self.list_search,
            self.list_range_search,
            self.list_editable,
        ):
            if item not in field_list:
                raise ValueError(f"field {item} not found in {field_list}")

        attrs = AdminInlineAttrs.model_validate(
            {
                "label": self.label,
                "help_text": self.help_text,
                "max_num": self.max_num,
                "min_num": self.min_num,
                "list_editable": self.list_editable,
                "list_filter": self.list_filter,
                "list_sort": self.list_sort,
                "list_order": self.list_order,
                "list_per_page": self.list_per_page,
                "list_per_page_options": self.list_per_page_options,
                "list_search": self.list_search,
                "list_range_search": self.list_range_search,
                "can_add": self.can_add,
                "can_delete": self.can_delete,
                "can_edit": self.can_edit,
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


class CustomAdmin(BaseAdmin):
    fields_set: t.List[CustomField] = []
    route_label: str = "Custom Pages"

    @property
    def permission_prefix(self) -> str:
        return f"custom.{self.__class__.__name__.lower()}"

    @property
    def view_permission(self) -> str:
        return f"{self.permission_prefix}.can_view"

    def action_permission(self, action: str) -> str:
        return f"{self.permission_prefix}.can_exec_{action}"

    def get_all_permissions(self) -> t.List[str]:
        return [
            self.view_permission,
        ] + [self.action_permission(action) for action in self.get_actions()]  # type: ignore

    @t.override
    def to_serialize(self) -> AdminCustomSerializeModel:
        fields_map = {}
        for field in self.fields_set:
            fields_map[field.name] = field.to_json()

        attrs = AdminCustomAttrs(help_text=self.help_text)

        actions = self.get_actions()

        return AdminCustomSerializeModel(
            fields=fields_map,
            actions=actions,
            attrs=attrs,
        )
