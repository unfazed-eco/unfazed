import typing as t

from pydantic import BaseModel, Field


class AdminField(BaseModel):
    field_type: str = Field(..., alias="type")
    readonly: bool = False
    show: bool = False
    blank: bool = True
    choices: t.List[t.Tuple[str, str]] = []
    help_text: str = ""
    default: t.Any = None


class AdminAttrs(BaseModel):
    editable: bool = True
    help_text: t.List[str] = []
    can_show_all: bool = True
    can_search: bool = True
    search_fields: t.List[str] = []
    list_per_page: int = 20
    detail_display: t.List[str] = []
    can_add: bool = True
    list_search: t.List[str] = []
    can_delete: bool = True
    can_edit: bool = True
    list_filter: t.List[str] = []
    list_sort: t.List[str] = []


class AdminAction(BaseModel):
    name: str
    raw_name: str
    output: int
    confirm: bool
    description: str
    batch: bool
    extra: t.Dict[str, t.Any]


class AdminSerializeModel(BaseModel):
    fields: t.Dict[str, AdminField]
    actions: t.Dict[str, AdminAction]
    attrs: AdminAttrs
