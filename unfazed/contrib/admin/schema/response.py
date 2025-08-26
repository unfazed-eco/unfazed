import typing as t

from unfazed.contrib.admin.registry.schema import (
    AdminCustomSerializeModel,
    AdminInlineSerializeModel,
    AdminSerializeModel,
    AdminSite,
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


class DescResp(BaseResponse[t.Union[AdminSerializeModel, AdminCustomSerializeModel]]):
    pass


class InlinesResp(BaseResponse[t.Dict[str, AdminInlineSerializeModel]]):
    pass


class DataResp(BaseResponse[Result]):
    pass


class SaveResp(BaseResponse[t.Dict]):
    pass


class DeleteResp(BaseResponse[t.Dict]):
    pass
