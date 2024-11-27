import typing as t
from functools import cached_property

from tortoise import Model

from unfazed.http import HttpRequest
from unfazed.protocol import BaseAdmin

from .models import AbstractUser


class AuthMixin(BaseAdmin):
    @cached_property
    def model_description(self) -> t.Dict[str, t.Any]:
        model: Model = self.serializer.Meta.model
        return model.describe()

    @property
    def permission_prefix(self):
        return f"{self.model_description['app']}.{self.model_description['table']}"

    @property
    def view_permission(self) -> str:
        return f"{self.permission_prefix}.can_view"

    @property
    def change_permission(self) -> str:
        return f"{self.permission_prefix}.can_change"

    @property
    def delete_permission(self) -> str:
        return f"{self.permission_prefix}.can_delete"

    @property
    def create_permission(self) -> str:
        return f"{self.permission_prefix}.can_create"

    def action_permission(self, action: str) -> str:
        return f"{self.permission_prefix}.can_exec_{action}"

    def get_all_permissions(self) -> t.List[str]:
        return [
            self.view_permission,
            self.change_permission,
            self.delete_permission,
            self.create_permission,
        ] + [self.action_permission(action) for action in self.get_actions()]

    async def has_view_permission(self, request: HttpRequest, *args, **kw) -> bool:
        user: AbstractUser = request.user
        return await user.has_permission(self.view_permission)

    async def has_change_permission(self, request: HttpRequest, *args, **kw) -> bool:
        user: AbstractUser = request.user
        return await user.has_permission(self.change_permission)

    async def has_delete_permission(self, request: HttpRequest, *args, **kw) -> bool:
        user: AbstractUser = request.user
        return await user.has_permission(self.delete_permission)

    async def has_create_permission(self, request: HttpRequest, *args, **kw) -> bool:
        user: AbstractUser = request.user
        return await user.has_permission(self.create_permission)

    async def has_action_permission(
        self, request: HttpRequest, action: str, *args, **kw
    ) -> bool:
        user: AbstractUser = request.user
        return await user.has_permission(self.action_permission(action))
