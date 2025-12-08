import typing as t
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from unfazed.contrib.admin.settings import AuthPlugin
from unfazed.http import HttpRequest
from unfazed.type import Doc

ShowStr = t.Annotated[str, Doc(description="show in frontend admin")]
ActualStr = t.Annotated[str, Doc(description="actual value")]


class AutoFill(BaseModel):
    pass


class AdminThrough(BaseModel):
    through: str = Field(description="mid model name")

    source_field: str = Field(description="source field name")
    source_to_through_field: str = Field(description="source to through field name")

    target_field: str = Field(description="target field name")
    target_to_through_field: str = Field(description="target to through field name")


class AdminRelation(BaseModel):
    target: str = Field(description="target Admin name")

    source_field: str | AutoFill = Field(
        default=AutoFill(), description="source field name"
    )

    target_field: str | AutoFill = Field(
        default=AutoFill(), description="target field name"
    )

    relation: t.Literal["fk", "o2o", "m2m", "bk_fk", "bk_o2o"] | AutoFill = Field(
        default=AutoFill(), description="relation type"
    )

    through: t.Optional[AdminThrough] = Field(
        default=None, description="through model name"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ActionOutput(StrEnum):
    Download = "download"
    Refresh = "refresh"
    Toast = "toast"
    Display = "display"


class ActionInput(StrEnum):
    Empty = "empty"
    String = "string"
    File = "file"


class AdminField(BaseModel):
    field_type: t.Literal[
        "CharField",
        "IntegerField",
        "BooleanField",
        "FloatField",
        "DateField",
        "DatetimeField",
        "TimeField",
        "TextField",
        "EditorField",
        "ImageField",
        "UploadField",
        "JsonField",
    ] = Field(
        ...,
        alias="type",
        description="type of this field, different field types map to different frontend components",
    )
    readonly: bool = Field(
        default=False,
        description="readonly for this field, frontend admin will not allow user to edit this field",
    )
    show: bool = Field(default=True, description="show in frontend admin")
    blank: bool = Field(
        default=True,
        description="frontend admin will not require this field if blank is True",
    )
    choices: t.List[t.Tuple[t.Any, t.Any]] = Field(
        default_factory=list,
        description="choices for this field, frontend admin will show the show value",
    )
    help_text: str = Field(
        description="help text for this field, frontend admin will show the help text"
    )
    default: t.Any = Field(
        default=None,
        description="default value for this field, frontend admin will show the show value",
    )
    name: str | None = Field(default=None, description="name of this field")


class AdminBaseAttrs(BaseModel):
    help_text: str = Field(
        default="",
        description="help text for this attribute, frontend admin will show the help text",
    )

    # action related
    can_add: bool = Field(
        default=True,
        description="Will show a Add button in frontend admin if can_add is True",
    )
    can_delete: bool = Field(
        default=True,
        description="Will show a Delete button in frontend admin if can_delete is True",
    )
    can_edit: bool = Field(
        default=True,
        description="the data can be edited inlines",
    )
    list_per_page: int = Field(
        default=20, description="number of items to display per page in frontend admin"
    )
    list_per_page_options: t.List[int] = Field(
        default=[10, 20, 50, 100],
        description="list of options for number of items to display per page in frontend admin",
    )
    list_search: t.List[str] = Field(
        default_factory=list,
        description="list of fields to search in frontend admin, frontend behavior",
    )
    list_range_search: t.List[str] = Field(
        default_factory=list,
        description="list of fields to range search in frontend admin, frontend behavior",
    )
    list_filter: t.List[str] = Field(
        default_factory=list,
        description="list of fields to filter in frontend admin, frontend behavior",
    )
    list_sort: t.List[str] = Field(
        default_factory=list,
        description="list of fields to sort in frontend admin, frontend behavior",
    )
    list_order: t.List[str] = Field(
        default_factory=list,
        description="list of fields to order in frontend admin, frontend behavior",
    )
    list_editable: t.List[str] = Field(
        default_factory=list,
        description="list of fields to edit in frontend admin, frontend behavior",
    )


class AdminAttrs(AdminBaseAttrs):
    # detail related
    detail_editable: t.List[str] = Field(
        default_factory=list,
        description="list of fields to edit in frontend admin, frontend behavior",
    )
    detail_display: t.List[str] = Field(
        default_factory=list,
        description="list of fields to display in frontend admin, frontend behavior",
    )

    detail_order: t.List[str] = Field(
        default_factory=list,
        description="list of fields to order in frontend admin, frontend behavior",
    )


class AdminInlineAttrs(AdminBaseAttrs):
    # list page control
    max_num: int = Field(
        default=0,
        description="max number of items to edit in frontend admin",
    )
    min_num: int = Field(
        default=0,
        description="min number of items to edit in frontend admin",
    )
    label: str = Field(
        default="",
        description="label of this inline, displayed in frontend admin",
    )


class AdminCustomAttrs(BaseModel):
    help_text: str = Field(
        default="",
        description="help text for this tool, frontend admin will show the help text",
    )


class AdminAction(BaseModel):
    name: str = Field(description="name of this action")
    label: str = Field(description="label of this action, displayed in frontend admin")
    output: ActionOutput = Field(
        default=ActionOutput.Toast, description="output of this action"
    )
    input: ActionInput = Field(
        default=ActionInput.Empty, description="input of this action"
    )
    confirm: bool = Field(default=False, description="whether to confirm this action")
    description: str = Field(description="description of this action")
    batch: bool = Field(description="whether a batch action")
    extra: t.Dict[str, t.Any] = Field(
        default_factory=dict,
        description="extra data for this action, extention for future use",
    )


class BaseAdminSerializeModel(BaseModel):
    fields: t.Dict[str, AdminField] = Field(
        description="fields of this model, frontend admin will show the fields",
    )
    actions: t.Dict[str, AdminAction] = Field(
        description="actions of this model, frontend admin will show the actions",
    )


class AdminSerializeModel(BaseAdminSerializeModel):
    attrs: AdminAttrs = Field(
        description="attrs of this model, frontend admin will build the page according to the attrs",
    )


class AdminInlineSerializeModel(BaseAdminSerializeModel):
    attrs: AdminInlineAttrs = Field(
        description="attrs of this model, frontend admin will build the page according to the attrs",
    )
    relation: t.Optional[AdminRelation] = Field(
        default=None,
        description="relation of this model, frontend admin will show the relation",
    )


class AdminCustomSerializeModel(BaseAdminSerializeModel):
    attrs: AdminCustomAttrs = Field(
        description="attrs of this model, frontend admin will build the page according to the attrs",
    )


class AdminSite(BaseModel):
    title: str = Field(description="title of this admin site")
    navTheme: str = Field(description="nav theme of this admin site")
    colorPrimary: str = Field(description="color primary of this admin site")
    layout: str = Field(description="layout of this admin site")
    contentWidth: str = Field(description="content width of this admin site")
    fixedHeader: bool = Field(description="fixed header of this admin site")
    fixSiderbar: bool = Field(description="fix siderbar of this admin site")
    pwa: bool = Field(description="pwa of this admin site")
    iconfontUrl: str = Field(description="iconfont url of this admin site")
    colorWeak: bool = Field(description="color weak of this admin site")
    logo: str = Field(description="logo of this admin site")
    pageSize: int = Field(description="page size of this admin site")
    timeZone: str = Field(description="time zone of this admin site")
    debug: bool = Field(description="debug of this admin site")
    version: str = Field(description="version of this admin site")
    showWatermark: bool = Field(description="show watermark of this admin site")
    extra: t.Dict[str, t.Any] = Field(
        default_factory=dict,
        description="extra data for this admin site",
    )
    # TODO
    # Need to agree with the frontend on what type this is
    authPlugins: t.List[AuthPlugin] = Field(
        default_factory=list,
        description="auth plugins of this admin site",
    )
    defaultLoginType: bool = Field(
        default=False,
        description="default login type of this admin site",
    )
    websitePrefix: str = Field(
        default="/admin",
        description="website prefix of this admin site",
    )
    apiPrefix: str = Field(
        default="/api/contrib/admin",
        description="api prefix of this admin site",
    )


class ActionKwargs(BaseModel):
    search_condition: t.Dict[str, t.Any] = Field(
        default_factory=dict,
        description="search condition of this action",
    )
    form_data: t.Dict[str, t.Any] = Field(
        default_factory=dict,
        description="form data of this action",
    )

    input_data: t.Dict[str, t.Any] = Field(
        default_factory=dict,
        description="input data of this action",
    )

    request: HttpRequest | None = Field(
        default=None,
        description="request of this action",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)
