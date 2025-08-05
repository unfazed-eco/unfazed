import typing as t

from pydantic import BaseModel, Field

from unfazed.contrib.admin.registry.schema import (
    AdminInlineSerializeModel,
    AdminSerializeModel,
    AdminSite,
    AdminToolSerializeModel,
)
from unfazed.contrib.common.schema import BaseResponse
from unfazed.schema import AdminRoute, Result

ModelLineDataT = t.TypeVar("ModelLineDataT", bound=t.Dict[str, t.Any])


# route
class RouteResp(BaseResponse[t.List[AdminRoute]]):
    pass


# site settings
class SiteSettingsResp(BaseResponse[AdminSite]):
    pass


class DescResp(BaseResponse[t.Union[AdminSerializeModel, AdminToolSerializeModel]]):
    pass


class DetailData(BaseModel):
    inlines: t.Dict[str, AdminInlineSerializeModel] = Field(
        description="inlines for this model"
    )


class DetailResp(BaseResponse[DetailData]):
    pass


class DataResp(BaseResponse[Result[ModelLineDataT]]):
    pass


class SaveResp(BaseResponse[t.Dict]):
    pass


class DeleteResp(BaseResponse[t.Dict]):
    pass
