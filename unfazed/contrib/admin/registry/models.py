import enum
import typing as t

from pydantic import BaseModel as PydanticModel
from pydantic import Field
from pydantic.fields import FieldInfo

from unfazed.db.tortoise.serializer import TSerializer
from unfazed.http import HttpRequest


class AdminField(PydanticModel):
    field_type: str = Field(..., alias="type")
    readonly: bool = False
    show: bool = False
    blank: bool = True
    choices: t.List[t.Tuple[str, str]] = []
    help_text: str = ""
    default: t.Any = None


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

    def get_actions(self) -> t.Dict[str, t.Dict]:
        actions: t.Dict[str, t.Dict] = {}
        for ele in dir(self):
            if hasattr(ele, "action"):
                attrs = ele.attrs
                actions[attrs["name"]] = attrs

        return actions

    def get_batch_actions(self) -> t.Dict[str, t.Dict]:
        actions: t.Dict[str, t.Dict] = {}
        for ele in dir(self):
            if hasattr(ele, "batch_action"):
                attrs = ele.attrs
                actions[attrs["name"]] = attrs

        return actions

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
    serializer: t.Annotated[TSerializer, "also a pydantic model"]

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

            json_schema_extra = getattr(fieldinfo, "json_schema_extra", {})
            choices = json_schema_extra.get("choices", [])

            fields_mapping[name] = AdminField(
                **{
                    "type": field_class_name,
                    "readonly": False,
                    "show": False,
                    "blank": True,
                    "choices": choices,
                    "help_text": fieldinfo.description,
                    "default": fieldinfo.default,
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
            fields_mapping[item].black = False

        return fields_mapping

    def get_attributes(self) -> t.Dict[str, t.Any]:
        pass


class ToolAdmin(BaseModel):
    pass


class CacheAdmin(BaseModel):
    pass
