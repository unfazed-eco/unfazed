import inspect
import typing as t

from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from tortoise import Model as TModel

from unfazed.contrib.admin.registry.schema import AdminSite
from unfazed.exception import PermissionDenied
from unfazed.http import HttpRequest
from unfazed.schema import AdminRoute, Condition, Result
from unfazed.serializer import Serializer
from unfazed.type import Doc

from .registry import (
    ActionKwargs,
    AdminCustomSerializeModel,
    AdminInlineSerializeModel,
    AdminSerializeModel,
    CustomAdmin,
    ModelAdmin,
    ModelInlineAdmin,
    admin_collector,
    parse_cond,
    site,
)
from .schema import Action


class IdSchema(BaseModel):
    id: int = 0


class AdminModelService:
    @classmethod
    async def list_route(cls, request: HttpRequest) -> t.List[AdminRoute]:
        temp = {}

        admin_ins: t.Union[ModelAdmin, ModelInlineAdmin, CustomAdmin]
        for _, admin_ins in admin_collector:
            if not await admin_ins.has_view_perm(request):
                continue

            route = admin_ins.to_route()

            if not route:
                continue

            if isinstance(admin_ins, ModelAdmin):
                m: t.Type[TModel] = admin_ins.serializer.Meta.model
                route_label = admin_ins.route_label or m._meta.app or "Default"
            else:
                route_label = admin_ins.route_label or "Default"

            route_label = route_label.capitalize()

            if route_label not in temp:
                temp_top_route = AdminRoute(
                    name=route_label,
                    label=route_label,
                    path=f"/{route_label.replace(' ', '-')}",
                    routes=[],
                    icon="",
                    hideInMenu=False,
                    hideChildrenInMenu=False,
                )
                temp[route_label] = temp_top_route
            else:
                temp_top_route = temp[route_label]
            temp_top_route.routes.append(route)

        routes = []

        sub_route: BaseModel
        for _, sub_route in temp.items():
            routes.append(sub_route)

        return routes

    @classmethod
    def site_settings(cls) -> AdminSite:
        return site.to_serialize()

    @classmethod
    async def model_desc(
        cls, admin_ins_name: str, request: HttpRequest
    ) -> t.Union[AdminSerializeModel, AdminCustomSerializeModel]:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_view_perm(request):
            raise PermissionDenied(message="Permission Denied")

        return admin_ins.to_serialize()

    @classmethod
    async def model_inlines(
        cls, admin_ins_name: str, data: t.Dict[str, t.Any], request: HttpRequest
    ) -> t.Dict[str, AdminInlineSerializeModel]:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_view_perm(request):
            raise PermissionDenied(message="Permission Denied")

        return admin_ins.to_inlines()

    @classmethod
    async def model_data(
        cls,
        admin_ins_name: str,
        cond: t.List[Condition],
        page: int,
        size: int,
        request: HttpRequest,
    ) -> Result:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_view_perm(request):
            raise PermissionDenied(message="Permission Denied")

        cond = parse_cond(condtion=cond)
        serializer_cls: t.Type[Serializer] = admin_ins.serializer
        queryset = serializer_cls.get_queryset(cond, fetch_relations=False)
        result: Result = await serializer_cls.list(queryset, page, size)

        return result

    @classmethod
    async def model_action(
        cls,
        ctx: Action,
        request: HttpRequest | None = None,
    ) -> t.Any:
        admin_ins: ModelAdmin = admin_collector[ctx.name]
        if not hasattr(admin_ins, ctx.action):
            raise KeyError(
                f"admin ins {admin_ins.name} does not have action {ctx.action}"
            )

        if request is not None and not await admin_ins.has_action_perm(request):
            raise PermissionDenied(message="Permission Denied")

        method = getattr(admin_ins, ctx.action)
        cond_dict = parse_cond(condtion=ctx.search_condition)

        ctx = ActionKwargs(
            search_condition=cond_dict,
            form_data=ctx.form_data,
            input_data=ctx.input_data,
            request=request,
        )
        if inspect.iscoroutinefunction(method):
            return await method(ctx=ctx)
        return await run_in_threadpool(method, ctx=ctx)

    @classmethod
    async def model_save(
        cls, admin_ins_name: str, data: t.Dict, request: HttpRequest
    ) -> t.Annotated[
        Serializer,
        Doc(description="return the saved model inherited by BaseSerializer"),
    ]:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_change_perm(
            request
        ) and not await admin_ins.has_create_perm(request):
            raise PermissionDenied(message="Permission Denied")

        serializer_cls: t.Type[Serializer] = admin_ins.serializer

        # handle main model
        idschema = IdSchema.model_validate(data)
        if idschema.id <= 0:
            serializer = serializer_cls.model_validate(data)
            db_ins = await serializer.create()
        else:
            current_db_ins = await serializer_cls.get_object(idschema)
            serializer = serializer_cls.model_validate(data)
            db_ins = await serializer.update(current_db_ins)

        return await serializer_cls.retrieve(db_ins)

    @classmethod
    async def model_delete(
        cls,
        admin_ins_name: str,
        data: t.Dict,
        request: HttpRequest,
    ) -> None:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_delete_perm(request):
            raise PermissionDenied(message="Permission Denied")

        idschema = IdSchema(**data)

        if idschema.id <= 0:
            raise ValueError("id must be greater than 0")

        serializer_cls: t.Type[Serializer] = admin_ins.serializer
        db_model = await serializer_cls.get_object(idschema)

        # TODO: handle related data

        return await serializer_cls.destroy(db_model)
