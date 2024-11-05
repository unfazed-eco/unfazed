import typing as t

from pydantic import BaseModel

from unfazed.route import params as p
from unfazed.type import Doc


class BaseResp(BaseModel):
    code: int = 0
    message: str = ""


class DescField(BaseModel):
    blank: bool
    choices: list
    default: str | None
    help_text: str
    readonly: bool
    show: bool
    type: str


class DescAttr(BaseModel):
    can_add: bool
    can_search: bool
    can_showall: bool
    help_text: str
    list_filter: list
    list_per_page: int
    list_search: list
    list_sort: list


class DescAction(BaseResp):
    name: str
    help_text: str
    confirm: bool


class DescBatchAction(DescAction):
    pass


class DescData(BaseModel):
    fields: dict[str, DescField]
    attrs: DescAttr
    actions: dict[str, DescAction]
    batch_actions: dict[str, DescBatchAction]


class DescResp(BaseResp):
    data: DescData


DESC_RESP = [p.ResponseSpec(model=DescResp, description="Model Description")]


class DetailInlineData(BaseModel):
    actions: dict[str, DescAction]
    attrs: DescAttr
    fields: dict[str, DescField]


class DetailData(BaseModel):
    inlines: t.Dict[str, DetailInlineData]


class DetailResp(BaseResp):
    data: DetailData


DETAIL_RESP = [p.ResponseSpec(model=DetailData, description="Model relations detail")]


class DataResp(BaseResp):
    data: t.List[t.Annotated[t.Dict, Doc(description="depends on the tortoise model")]]


DATA_RESP = [p.ResponseSpec(model=DataResp, description="query data from model")]


class SaveResp(BaseResp):
    data: t.Dict = {}


SAVE_RESP = [p.ResponseSpec(model=SaveResp, description="save data to model")]


class DeleteResp(BaseResp):
    data: t.Dict = {}


DELETE_RESP = [p.ResponseSpec(model=DeleteResp, description="delete data to model")]
