import inspect
import typing as t

from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from unfazed.exception import PermissionDenied
from unfazed.http import HttpRequest
from unfazed.protocol import BaseSerializer
from unfazed.schema import AdminRoute, Condtion

from .registry import (
    BaseAdmin,
    ModelAdmin,
    admin_collector,
    parse_cond,
    site,
)


class IdSchema(BaseModel):
    id: int = 0


class InlineStatus:
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    NO_ACTION = "no_action"


class AdminModelService:
    @classmethod
    async def list_route(cls, request: HttpRequest) -> t.List[t.Dict]:
        temp = {}
        admin_ins: BaseAdmin
        for _, admin_ins in admin_collector:
            if not await admin_ins.has_view_perm(request):
                continue

            route = admin_ins.to_route()

            if not route:
                continue

            if isinstance(admin_ins, ModelAdmin):
                route_label = (
                    admin_ins.route_label
                    or admin_ins.serializer.Meta.model._meta.app
                    or "Default"
                )
            else:
                route_label = admin_ins.route_label or "Default"

            route_label = route_label.capitalize()

            if route_label not in temp:
                temp_top_route = AdminRoute(
                    title=route_label,
                    children=[],
                    name=route_label,
                    icon="el-icon-s-home",
                    meta={
                        "icon": "el-icon-s-home",
                        "hidden": False,
                        "hidden_children": False,
                    },
                )
                temp[route_label] = temp_top_route
            else:
                temp_top_route = temp[route_label]
            temp_top_route.children.append(route)

        routes = []

        route: BaseModel
        for _, route in temp.items():
            routes.append(route.model_dump(exclude_none=True))

        return routes

    @classmethod
    def site_settings(cls) -> t.Dict:
        return site.to_serialize().model_dump(exclude_none=True)

    @classmethod
    async def model_desc(cls, admin_ins_name: str, request: HttpRequest) -> t.Dict:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_view_perm(request):
            raise PermissionDenied(message="Permission Denied")

        return admin_ins.to_serialize().model_dump(exclude_none=True)

    @classmethod
    async def model_detail(
        cls, admin_ins_name: str, data: t.Dict[str, t.Any], request: HttpRequest
    ) -> t.Dict:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_view_perm(request):
            raise PermissionDenied(message="Permission Denied")

        return admin_ins.to_inlines()

    @classmethod
    async def model_data(
        cls,
        admin_ins_name: str,
        cond: t.List[Condtion],
        page: int,
        size: int,
        request: HttpRequest,
    ) -> t.Dict:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_view_perm(request):
            raise PermissionDenied(message="Permission Denied")

        cond = parse_cond(condtion=cond)
        serializer_cls: t.Type[BaseSerializer] = admin_ins.serializer
        queryset = serializer_cls.get_queryset(cond, fetch_related=False)
        result: BaseModel = await serializer_cls.list(queryset, page, size)

        return result.model_dump(exclude_none=True)

    @classmethod
    async def model_action(
        cls,
        admin_ins_name: str,
        action: str,
        data: t.Dict,
        request: HttpRequest | None = None,
    ) -> t.Any:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]
        if not hasattr(admin_ins, action):
            raise KeyError(f"admin ins {admin_ins.name} does not have action {action}")

        if not await admin_ins.has_action_perm(request):
            raise PermissionDenied(message="Permission Denied")

        method = getattr(admin_ins, action)

        if inspect.iscoroutinefunction(method):
            return await method(data, request)
        return await run_in_threadpool(method, data, request)

    @classmethod
    async def model_save(
        cls, admin_ins_name: str, data: t.Dict, inlines: t.Dict, request: HttpRequest
    ) -> t.Dict:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_change_perm(
            request
        ) and not await admin_ins.has_create_perm(request):
            raise PermissionDenied(message="Permission Denied")

        serializer_cls: t.Type[BaseSerializer] = admin_ins.serializer

        # handle main model
        idschema = IdSchema(**data)
        if idschema.id <= 0:
            serializer = serializer_cls(**data)
            db_ins = await serializer.create()
        else:
            current_db_ins = await serializer_cls.get_object(idschema)
            serializer = serializer_cls(**data)
            db_ins = await serializer.update(current_db_ins)

        # handle inlines
        for name, inline_data_list in inlines.items():
            ins = admin_collector[name]
            inline_serializer_cls: t.Type[BaseSerializer] = ins.serializer
            relation = inline_serializer_cls.find_relation(serializer_cls)

            if not relation:
                raise ValueError(
                    f"relation between {name} and {admin_ins_name} not found"
                )

            for inline_data in inline_data_list:
                stat = inline_data.pop("__status", "no_action")
                ins_idschema = IdSchema(**inline_data)

                # m2m
                if relation.relation == "m2m":
                    if stat == InlineStatus.DELETE:
                        inline_db_ins = await inline_serializer_cls.get_object(
                            ins_idschema
                        )
                        await getattr(inline_db_ins, relation.source_field).remove(
                            db_ins
                        )
                    elif stat == InlineStatus.CREATE:
                        serializer = inline_serializer_cls(**inline_data)
                        inline_db_ins = await serializer.create()
                        await getattr(inline_db_ins, relation.source_field).add(db_ins)
                    elif stat == InlineStatus.UPDATE:
                        inline_db_ins = await inline_serializer_cls.get_object(
                            ins_idschema
                        )
                        serializer = inline_serializer_cls(**inline_data)
                        await serializer.update(inline_db_ins)

                    else:
                        pass  # do nothing

                # fk
                elif relation.relation == "fk":
                    if stat == InlineStatus.DELETE:
                        inline_db_ins = await inline_serializer_cls.get_object(
                            ins_idschema
                        )
                        await inline_serializer_cls.destroy(inline_db_ins)
                    elif stat == InlineStatus.CREATE:
                        inline_data[relation.source_field] = getattr(
                            db_ins, relation.dest_field
                        )
                        serializer = inline_serializer_cls(**inline_data)
                        await serializer.create()

                    elif stat == InlineStatus.UPDATE:
                        old_inline_db_ins = await inline_serializer_cls.get_object(
                            ins_idschema
                        )
                        serializer = inline_serializer_cls(**inline_data)
                        await serializer.update(old_inline_db_ins)

                    else:
                        pass  # do nothing

                # bk_fk
                elif relation.relation == "bk_fk":
                    raise ValueError("bk_fk relation does not support create")

                # o2o
                elif relation.relation == "o2o":
                    if stat == InlineStatus.DELETE:
                        inline_db_ins = await inline_serializer_cls.get_object(
                            ins_idschema
                        )
                        await inline_serializer_cls.destroy(inline_db_ins)
                    elif stat == InlineStatus.CREATE:
                        inline_data[relation.source_field] = getattr(
                            db_ins, relation.dest_field
                        )
                        serializer = inline_serializer_cls(**inline_data)
                        await serializer.create()
                    elif stat == InlineStatus.UPDATE:
                        inline_db_ins = await inline_serializer_cls.get_object(
                            ins_idschema
                        )
                        serializer = inline_serializer_cls(**inline_data)
                        await serializer.update(inline_db_ins)
                    else:
                        pass  # do nothing

                # bk_o2o
                else:
                    raise ValueError("bk_o2o relation does not support create")

        return await serializer_cls.retrieve(db_ins)

    @classmethod
    async def model_delete(
        cls, admin_ins_name: str, data: t.Dict, request: HttpRequest
    ) -> t.Any:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not await admin_ins.has_delete_perm(request):
            raise PermissionDenied(message="Permission Denied")

        idschema = IdSchema(**data)

        if idschema.id <= 0:
            raise ValueError("id must be greater than 0")

        serializer_cls: t.Type[BaseSerializer] = admin_ins.serializer
        db_model = await serializer_cls.get_object(idschema)

        return await serializer_cls.destroy(db_model)
