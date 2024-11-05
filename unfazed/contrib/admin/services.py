import typing as t

from unfazed.exception import PermissionDenied
from unfazed.http import HttpRequest
from unfazed.schema import Condtion

from .registry import BaseAdminModel, ModelAdmin, admin_collector, parse_cond, site


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
        ret = await admin_ins.serializer.list(cond, page, size)
        return ret

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
        return await admin_ins.serializer.create(data, inlines)

    @classmethod
    async def model_delete(
        cls, admin_ins_name: str, data: t.Dict, request: HttpRequest
    ) -> t.Any:
        admin_ins: ModelAdmin = admin_collector[admin_ins_name]

        if not admin_ins.has_delete_perm(request):
            raise PermissionDenied(message="Permission Denied")

        return await admin_ins.serializer.delete(data)
