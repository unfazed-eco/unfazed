import typing as t

from common.schema.request import account as ARQ
from common.schema.response import account as ARS

from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import params


# CRUD
async def list_account(
    request: HttpRequest, ctx: t.Annotated[ARQ.AccountQuery, params.Query()]
) -> t.Annotated[JsonResponse, ARS.SuccessfulQueryResp, ARS.FailedResp]:
    return JsonResponse({"message": "List account"})


async def retrieve_account(
    request: HttpRequest, ctx: t.Annotated[ARQ.AccountPath, params.Path()]
) -> t.Annotated[JsonResponse, ARS.SuccessfulCreateResp, ARS.FailedResp]:
    return JsonResponse({"message": "Retrieve account"})


async def create_account(
    request: HttpRequest,
    ctx: ARQ.AccountCreate,
    hdr: t.Annotated[ARQ.AccountHeader, params.Header()],
) -> t.Annotated[JsonResponse, ARS.SuccessfulCreateResp, ARS.FailedResp]:
    return JsonResponse({"message": "Create account"})


async def update_account(
    request: HttpRequest,
    ctx: ARQ.AccountUpdate,
    cookie: t.Annotated[ARQ.AccountCookie, params.Cookie()],
) -> t.Annotated[JsonResponse, ARS.SuccessfulUpdateResp, ARS.FailedResp]:
    return JsonResponse({"message": "Update account"})


async def delete_account(
    request: HttpRequest, ctx: t.Annotated[ARQ.AccountDelete, params.Json()]
) -> t.Annotated[JsonResponse, ARS.SuccessfulDeleteResp, ARS.FailedResp]:
    return JsonResponse({"message": "Delete account"})
