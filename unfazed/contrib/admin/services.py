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
    AdminInlineSerializeModel,
    AdminSerializeModel,
    AdminToolSerializeModel,
    ModelAdmin,
    ModelInlineAdmin,
    ToolAdmin,
    admin_collector,
    parse_cond,
    site,
)


class IdSchema(BaseModel):
    id: int = 0


class AdminModelService:
    @classmethod
    async def list_route(cls, request: HttpRequest) -> t.List[AdminRoute]:
        temp = {}

        admin_ins: t.Union[ModelAdmin, ModelInlineAdmin, ToolAdmin]
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
                    path=admin_ins.path,
                    routes=[],
                    icon="el-icon-s-home",
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
    ) -> t.Union[AdminSerializeModel, AdminToolSerializeModel]:
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
    ) -> t.Dict:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_view_perm(request):
            raise PermissionDenied(message="Permission Denied")

        cond = parse_cond(condtion=cond)
        serializer_cls: t.Type[Serializer] = admin_ins.serializer
        queryset = serializer_cls.get_queryset(cond, fetch_relations=False)
        result: Result = await serializer_cls.list(queryset, page, size)

        return result.model_dump(exclude_none=True)

    @classmethod
    async def model_action(
        cls,
        admin_ins_name: str,
        action: str,
        cond: t.List[Condition],
        extra: t.Dict[str, t.Any],
        request: HttpRequest,
    ) -> t.Any:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]
        if not hasattr(admin_ins, action):
            raise KeyError(f"admin ins {admin_ins.name} does not have action {action}")

        if not await admin_ins.has_action_perm(request):
            raise PermissionDenied(message="Permission Denied")

        method = getattr(admin_ins, action)
        cond_dict = parse_cond(condtion=cond)
        if inspect.iscoroutinefunction(method):
            return await method(cond_dict=cond_dict, extra=extra, request=request)
        return await run_in_threadpool(
            method, cond_dict=cond_dict, extra=extra, request=request
        )

    @classmethod
    async def model_save(
        cls, admin_ins_name: str, data: t.Dict, request: HttpRequest
    ) -> t.Annotated[
        t.Any, Doc(description="return the saved model inherited by BaseSerializer")
    ]:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_change_perm(
            request
        ) and not await admin_ins.has_create_perm(request):
            raise PermissionDenied(message="Permission Denied")

        serializer_cls: t.Type[Serializer] = admin_ins.serializer

        # handle main model
        idschema = IdSchema(**data)
        if idschema.id <= 0:
            serializer = serializer_cls(**data)
            db_ins = await serializer.create()
        else:
            current_db_ins = await serializer_cls.get_object(idschema)
            serializer = serializer_cls(**data)
            db_ins = await serializer.update(current_db_ins)

        return await serializer_cls.retrieve(db_ins)

    @classmethod
    async def model_delete(
        cls,
        admin_ins_name: str,
        data: t.Dict,
        strategy: t.Literal["set_null", "delete", "do_nothing"],
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
