import typing as t

from unfazed.contrib.auth.decorators import login_required
from unfazed.http import HttpRequest, HttpResponse, JsonResponse
from unfazed.route import params as p
from unfazed.type import Doc
from unfazed.utils import generic_response

from . import schema as s
from .decorators import record
from .services import AdminModelService


@login_required
async def list_route(
    request: HttpRequest,
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.RouteResp)]:
    ret = await AdminModelService.list_route(request)
    return JsonResponse(s.RouteResp(data=ret))


# @login_required
def settings(
    request: HttpRequest,
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.SiteSettingsResp)]:
    ret = AdminModelService.site_settings()
    return JsonResponse(s.SiteSettingsResp(data=ret))


@login_required
async def model_desc(
    request: HttpRequest, name: t.Annotated[str, p.Json()]
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.DescResp)]:
    ret = await AdminModelService.model_desc(name, request=request)
    return JsonResponse(s.DescResp(data=ret))


@login_required
async def model_inlines(
    request: HttpRequest, ctx: t.Annotated[s.Detail, p.Json()]
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.InlinesResp)]:
    ret = await AdminModelService.model_inlines(ctx.name, ctx.data, request=request)
    return JsonResponse(s.InlinesResp(data=ret))


@login_required
async def model_data(
    request: HttpRequest, ctx: t.Annotated[s.Data, p.Json()]
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.DataResp)]:
    ret = await AdminModelService.model_data(
        ctx.name, ctx.cond, ctx.page, ctx.size, request=request
    )
    return JsonResponse(s.DataResp(data=ret))


@login_required
@record
async def model_action(
    request: HttpRequest, ctx: t.Annotated[s.Action, p.Json()]
) -> t.Annotated[
    HttpResponse, Doc(description="depends on the action implemetion, text/json/stream")
]:
    ret = await AdminModelService.model_action(ctx, request)

    return generic_response(ret)


@login_required
@record
async def model_save(
    request: HttpRequest, ctx: t.Annotated[s.Save, p.Json()]
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.SaveResp)]:
    ret = await AdminModelService.model_save(ctx.name, ctx.data, request=request)

    return JsonResponse(s.SaveResp(data=ret.model_dump()))


@login_required
@record
async def model_delete(
    request: HttpRequest, ctx: t.Annotated[s.Delete, p.Json()]
) -> t.Annotated[JsonResponse, p.ResponseSpec(model=s.DeleteResp)]:
    await AdminModelService.model_delete(ctx.name, ctx.data, request=request)
    return JsonResponse(s.DeleteResp(data={}))
