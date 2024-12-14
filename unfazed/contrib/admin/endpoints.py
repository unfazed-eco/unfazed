import typing as t

from unfazed.contrib.auth.decorators import login_required
from unfazed.contrib.common.utils import response_success
from unfazed.http import HttpRequest, HttpResponse, JsonResponse
from unfazed.route import params as p
from unfazed.type import Doc
from unfazed.utils import generic_response

from . import schema as s
from .decorators import record
from .models import LogEntry
from .services import AdminModelService


@login_required
async def list_route(request: HttpRequest) -> JsonResponse:
    ret = await AdminModelService.list_route(request)

    await LogEntry.create(
        created_at=1, account="1", path="/", ip="1", request="1", response="1"
    )
    return response_success(data=ret)


@login_required
def settings(request: HttpRequest) -> JsonResponse:
    ret = AdminModelService.site_settings()
    return response_success(data=ret)


@login_required
async def model_desc(
    request: HttpRequest, name: t.Annotated[str, p.Json()]
) -> t.Annotated[JsonResponse, *s.DESC_RESP]:
    ret = await AdminModelService.model_desc(name, request=request)
    return response_success(data=ret)


@login_required
async def model_detail(
    request: HttpRequest, ctx: t.Annotated[s.Detail, p.Json()]
) -> t.Annotated[JsonResponse, *s.DETAIL_RESP]:
    ret = await AdminModelService.model_detail(ctx.name, ctx.data, request=request)
    return response_success(data=ret)


@login_required
async def model_data(
    request: HttpRequest, ctx: t.Annotated[s.Data, p.Json()]
) -> t.Annotated[JsonResponse, *s.DATA_RESP]:
    ret = await AdminModelService.model_data(
        ctx.name, ctx.cond, ctx.page, ctx.size, request=request
    )
    return response_success(data=ret)


@login_required
@record
async def model_action(
    request: HttpRequest, ctx: t.Annotated[s.Action, p.Json()]
) -> t.Annotated[
    HttpResponse, Doc(description="depends on the action implemetion, text/json/stream")
]:
    ret = await AdminModelService.model_action(ctx.name, ctx.action, ctx.data, request)

    return generic_response(ret)


@login_required
@record
async def model_save(
    request: HttpRequest, ctx: t.Annotated[s.Save, p.Json()]
) -> t.Annotated[JsonResponse, *s.SAVE_RESP]:
    ret = await AdminModelService.model_save(
        ctx.name, ctx.data, ctx.inlines, request=request
    )

    return response_success(data=ret)


@login_required
@record
async def model_delete(
    request: HttpRequest, ctx: t.Annotated[s.Delete, p.Json()]
) -> t.Annotated[JsonResponse, *s.DELETE_RESP]:
    await AdminModelService.model_delete(ctx.name, ctx.data, request=request)
    return response_success()
