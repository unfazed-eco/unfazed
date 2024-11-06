import typing as t

from pydantic import BaseModel

from unfazed.exception import PermissionDenied
from unfazed.http import HttpRequest

# from unfazed.db.tortoise.serializer import TSerializer
from unfazed.protocol import BaseSerializer
from unfazed.schema import Condtion

from .registry import BaseAdminModel, ModelAdmin, admin_collector, parse_cond, site


class IdSchema(BaseModel):
    id: int = 0


class AdminModelService:
    @classmethod
    async def list_route(cls) -> t.Dict:
        routes = admin_collector.get_routes()
        return routes

    @classmethod
    def site_settings(cls) -> t.Dict:
        return site.to_serialize()

    @classmethod
    def model_desc(cls, admin_ins_name: str, request: HttpRequest) -> t.Dict:
        admin_ins: BaseAdminModel = admin_collector[admin_ins_name]

        if not admin_ins.has_view_perm(request):
            raise PermissionDenied(message="Permission Denied")

        return admin_ins.to_serialize()

    @classmethod
    def model_detail(
        cls, admin_ins_name: str, data: t.Dict[str, t.Any], request: HttpRequest
    ) -> t.Dict:
        admin_ins: BaseAdminModel = admin_collector[admin_ins_name]

        if not admin_ins.has_view_perm(request):
            raise PermissionDenied(message="Permission Denied")

        return admin_ins.to_inlines(data)

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

        if not admin_ins.has_view_perm(request):
            raise PermissionDenied(message="Permission Denied")

        cond = parse_cond(condtion=cond)
        serializer_cls: t.Type[BaseSerializer] = admin_ins.serializer
        queryset = serializer_cls.get_queryset(cond, fetch_related=False)
        result: BaseModel = await serializer_cls.list(queryset, page, size)

        return result.model_dump()

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
            raise ValueError(
                f"admin ins {admin_ins.name} does not have action {action}"
            )

        if not admin_ins.has_action_perm(request):
            raise PermissionDenied(message="Permission Denied")

        method = getattr(admin_ins, action)

        return await method(data, request)

    @classmethod
    async def model_save(
        cls, admin_ins_name: str, data: t.Dict, inlines: t.Dict, request: HttpRequest
    ) -> t.Any:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not admin_ins.has_change_perm(request) and not admin_ins.has_create_perm(
            request
        ):
            raise PermissionDenied(message="Permission Denied")

        serializer_cls: t.Type[BaseSerializer] = admin_ins.serializer

        # handle main model
        idschema = IdSchema(**data)
        if idschema.id <= 0:
            serializer = serializer_cls(**data)
            db_ins = await serializer.create()
        else:
            db_obj = await serializer_cls.get_object(idschema)
            serializer = serializer_cls(**data)
            db_ins = await serializer.update(db_obj)

        # handle inlines
        for name, inline_data in inlines.items():
            # inlines_ins = admin_collector[name]
            # inline_serializer_cls = inline_ins.serializer
            # inline_stat = inline_data.pop("__status")

            # await inlines_serializer.create()
            pass

        return await serializer_cls.retrieve(db_ins)

    @classmethod
    async def model_delete(
        cls, admin_ins_name: str, data: t.Dict, request: HttpRequest
    ) -> t.Any:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not admin_ins.has_delete_perm(request):
            raise PermissionDenied(message="Permission Denied")

        idschema = IdSchema(**data)

        if idschema.id <= 0:
            raise ValueError("id must be greater than 0")

        serializer_cls: t.Type[BaseSerializer] = admin_ins.serializer
        db_model = await serializer_cls.get_object(idschema)

        return await serializer_cls.destroy(db_model)
