import typing as t

from pydantic import BaseModel, Field


class AdminField(BaseModel):
    field_type: str = Field(..., alias="type")
    readonly: bool = False
    show: bool = False
    blank: bool = True
    choices: t.List[t.Tuple[t.Any, t.Any]] = []
    help_text: str = ""
    default: t.Any = None
    name: str | None = None


class AdminBaseAttrs(BaseModel):
    help_text: t.List[str] = []

    # search panel
    can_search: bool = True
    search_fields: t.List[str] = []

    # action related
    can_add: bool = True
    can_delete: bool = True
    can_edit: bool = True

    # list related
    can_show_all: bool = True
    list_per_page: int = 20
    list_search: t.List[str] = []
    list_filter: t.List[str] = []
    list_sort: t.List[str] = []
    list_order: t.List[str] = []


class AdminAttrs(AdminBaseAttrs):
    # detail related
    editable: bool = True
    detail_display: t.List[str] = []


class AdminInlineAttrs(AdminBaseAttrs):
    # list page control
    max_num: int = 0
    min_num: int = 0

    can_copy: bool = False


class AdminToolAttrs(BaseModel):
    help_text: t.List[str] = []
    output_field: str


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
    attrs: t.Union[AdminAttrs, AdminInlineAttrs, AdminToolAttrs]


class AdminSite(BaseModel):
    title: str
    navTheme: str
    colorPrimary: str
    layout: str
    contentWidth: str
    fixedHeader: bool
    colorWeak: bool
    logo: str
    pageSize: int
    timeZone: str
    apiPrefix: str
    debug: bool
    version: str
    extra: t.Dict[str, t.Any]
    # TODO
    # Need to agree with the frontend on what type this is
    authPlugins: t.List[t.Dict[str, t.Any]]
