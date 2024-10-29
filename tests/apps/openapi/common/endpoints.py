import typing as t

from common.schema.request import account as ARQ
from common.schema.response import account as ARS

from unfazed.http import HttpRequest, JsonResponse
from unfazed.route import params


# CRUD
async def list_account(
    request: HttpRequest, ctx: t.Annotated[ARQ.AccountQuery, params.Query()]
) -> t.Annotated[JsonResponse[ARS._QueryResp], ARS.SuccessfulQueryResp, ARS.FailedResp]:
    pass


async def retrieve_account(
    request: HttpRequest, ctx: t.Annotated[ARQ.AccountPath, params.Path()]
) -> t.Annotated[
    JsonResponse[ARS._CreateResp], ARS.SuccessfulCreateResp, ARS.FailedResp
]:
    pass


async def create_account(
    request: HttpRequest,
    ctx: ARQ.AccountCreate,
    hdr: t.Annotated[ARQ.AccountHeader, params.Header()],
) -> t.Annotated[
    JsonResponse[ARS._CreateResp], ARS.SuccessfulCreateResp, ARS.FailedResp
]:
    pass


async def update_account(
    request: HttpRequest,
    ctx: ARQ.AccountUpdate,
    cookie: t.Annotated[ARQ.AccountCookie, params.Cookie()],
) -> t.Annotated[
    JsonResponse[ARS._UpdateResp], ARS.SuccessfulUpdateResp, ARS.FailedResp
]:
    pass


async def delete_account(
    request: HttpRequest, ctx: t.Annotated[ARQ.AccountDelete, params.Json()]
) -> t.Annotated[
    JsonResponse[ARS._UpdateResp], ARS.SuccessfulDeleteResp, ARS.FailedResp
]:
    pass
