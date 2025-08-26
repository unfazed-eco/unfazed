import typing as t

from unfazed.http import HttpRequest
from unfazed.protocol import AdminAuthProtocol

from .models import AbstractUser


class AuthMixin(AdminAuthProtocol):
    async def has_view_permission(
        self, request: HttpRequest, *args: t.Any, **kw: t.Any
    ) -> bool:
        user: AbstractUser = request.user
        return await user.has_permission(self.view_permission)

    async def has_change_permission(
        self, request: HttpRequest, *args: t.Any, **kw: t.Any
    ) -> bool:
        user: AbstractUser = request.user
        return await user.has_permission(self.change_permission)

    async def has_delete_permission(
        self, request: HttpRequest, *args: t.Any, **kw: t.Any
    ) -> bool:
        user: AbstractUser = request.user
        return await user.has_permission(self.delete_permission)

    async def has_create_permission(
        self, request: HttpRequest, *args: t.Any, **kw: t.Any
    ) -> bool:
        user: AbstractUser = request.user
        return await user.has_permission(self.create_permission)

    async def has_action_permission(
        self, request: HttpRequest, action: str, *args: t.Any, **kw: t.Any
    ) -> bool:
        user: AbstractUser = request.user
        return await user.has_permission(self.action_permission(action))
