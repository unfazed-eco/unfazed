import typing as t

from pydantic import BaseModel, Field

from unfazed.contrib.admin.registry.schema import AdminSite
from unfazed.contrib.common.schema import BaseResponse
from unfazed.schema import AdminRoute
from unfazed.type import Doc

ShowStr = t.Annotated[str, Doc(description="show in frontend admin")]
ActualStr = t.Annotated[str, Doc(description="actual value")]

ModelLineDataT = t.TypeVar("ModelLineDataT", bound=t.Dict[str, t.Any])


# route
class RouteResp(BaseResponse[t.List[AdminRoute]]):
    pass


# site settings
class SiteSettingsResp(BaseResponse[AdminSite]):
    pass


class DescField(BaseModel):
    blank: bool = Field(
        default=False,
        description="frontend admin will not require this field if blank is True",
    )
    choices: t.List[t.Tuple[ShowStr, ActualStr]] = Field(
        default_factory=list,
        description="choices for this field, frontend admin will show the show value",
    )
    default: str | None = Field(
        default=None,
        description="default value for this field, frontend admin will show the show value",
    )
    help_text: str = Field(
        description="help text for this field, frontend admin will show the help text",
    )
    readonly: bool = Field(
        default=False,
        description="readonly for this field, frontend admin will not allow user to edit this field",
    )
    show: bool = Field(default=True, description="show in frontend admin")
    type: str = Field(description="type of this field")


class DescAttr(BaseModel):
    can_add: bool = Field(
        default=True,
        description="can add in frontend admin",
    )
    can_search: bool = Field(
        default=True,
        description="can search in frontend admin",
    )
    can_showall: bool = Field(
        default=True, description="can show all in frontend admin"
    )
    help_text: str = Field(description="help text for this attribute")
    list_filter: t.List[str] = Field(
        default_factory=list, description="list of fields to filter in frontend admin"
    )
    list_per_page: int = Field(
        default=10, description="number of items to display per page in frontend admin"
    )
    list_search: t.List[str] = Field(
        default_factory=list, description="list of fields to search in frontend admin"
    )
    list_sort: t.List[str] = Field(
        default_factory=list, description="list of fields to sort in frontend admin"
    )


class DescAction(BaseModel):
    name: str = Field(description="name of this action")
    help_text: str = Field(description="help text for this action")
    confirm: bool = Field(
        default=False, description="confirm before executing this action"
    )


class DescBatchAction(DescAction):
    pass


class DescData(BaseModel):
    fields: t.Dict[str, DescField] = Field(description="fields for this model")
    attrs: DescAttr = Field(description="attributes for this model")
    actions: t.Dict[str, DescAction] = Field(description="actions for this model")
    batch_actions: t.Dict[str, DescBatchAction] = Field(
        description="batch actions for this model"
    )


class DescResp(BaseResponse[DescData]):
    pass


class DetailInlineData(BaseModel):
    actions: t.Dict[str, DescAction] = Field(description="actions for inline model")
    attrs: DescAttr = Field(description="attributes for inline model")
    fields: t.Dict[str, DescField] = Field(description="fields for inline model")


class DetailData(BaseModel):
    inlines: t.Dict[str, DetailInlineData] = Field(description="inlines for this model")


class DetailResp(BaseResponse[DetailData]):
    pass


class DataResp(
    BaseResponse[
        t.List[
            t.Annotated[
                ModelLineDataT, Doc(description="depends on the tortoise model")
            ]
        ]
    ]
):
    pass


class SaveResp(BaseResponse[t.Dict]):
    pass


class DeleteResp(BaseResponse[t.Dict]):
    pass
