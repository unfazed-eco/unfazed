import typing as t

from unfazed.contrib.auth.decorators import login_required
from unfazed.http import HttpRequest, HttpResponse, JsonResponse
from unfazed.route import params as p
from unfazed.type import Doc

from . import schema as s
from .decorators import record
from .services import AdminModelService

_ = t.Annotated


@login_required
async def list_route(request: HttpRequest) -> JsonResponse:
    ret = await AdminModelService.list_route()
    return JsonResponse(ret)


@login_required
def settings(request: HttpRequest) -> JsonResponse:
    ret = AdminModelService.site_settings()
    return JsonResponse(ret)


@login_required
async def model_desc(
    request: HttpRequest, name: _[str, p.Json()]
) -> _[JsonResponse[s.DescResp], *s.DESC_RESP]:
    ret = AdminModelService.model_desc(name)
    return JsonResponse(ret)


@login_required
async def model_detail(
    request: HttpRequest, ctx: _[s.Detail, p.Json()]
) -> _[JsonResponse[s.DetailResp], *s.DETAIL_RESP]:
    ret = AdminModelService.model_detail(ctx.name, ctx.data)
    return JsonResponse(ret)


@login_required
async def model_data(
    request: HttpRequest, ctx: _[s.Data, p.Json()]
) -> _[JsonResponse[s.DataResp], *s.DATA_RESP]:
    ret = await AdminModelService.model_data(ctx.name, ctx.cond, ctx.page, ctx.size)
    return JsonResponse(ret)


@login_required
@record
async def model_action(
    request: HttpRequest, ctx: _[s.Action, p.Json()]
) -> t.Annotated[
    HttpResponse, Doc("depends on the action implemetion, text/json/stream")
]:
    ret = await AdminModelService.model_action(ctx.name, ctx.action, ctx.data, request)
    return JsonResponse(ret)


@login_required
@record
async def model_save(
    request: HttpRequest, ctx: _[s.Save, p.Json()]
) -> _[JsonResponse[s.SaveResp], *s.SAVE_RESP]:
    ret = await AdminModelService.model_save(ctx.name, ctx.data, ctx.inlines)
    return JsonResponse(ret)


@login_required
@record
async def model_delete(
    request: HttpRequest, ctx: _[s.Delete, p.Json()]
) -> _[JsonResponse[s.DeleteResp], *s.DELETE_RESP]:
    ret = await AdminModelService.model_delete(ctx.name, ctx.data)
    return JsonResponse(ret)
