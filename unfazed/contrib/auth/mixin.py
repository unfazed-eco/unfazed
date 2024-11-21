import typing as t

from tortoise import Model

from unfazed.http import HttpRequest
from unfazed.protocol import BaseAdmin

from .models import AbstractUser


class AuthMixin(BaseAdmin):
    @property
    def view_permission(self) -> str:
        model: Model = self.serializer.Meta.model
        return f"{model._meta.app_label}.{model._meta.model_name}.can_view"

    @property
    def change_permission(self) -> str:
        model: Model = self.serializer.Meta.model
        return f"{model._meta.app_label}.{model._meta.model_name}.can_change"

    @property
    def delete_permission(self) -> str:
        model: Model = self.serializer.Meta.model
        return f"{model._meta.app_label}.{model._meta.model_name}.can_delete"

    @property
    def create_permission(self) -> str:
        model: Model = self.serializer.Meta.model
        return f"{model._meta.app_label}.{model._meta.model_name}.can_create"

    def action_permission(self, action: str) -> str:
        model: Model = self.serializer.Meta.model
        return f"{model._meta.app_label}.{model._meta.model_name}.can_use_{action}"

    def get_all_permissions(self) -> t.List[str]:
        return [
            self.view_permission,
            self.change_permission,
            self.delete_permission,
            self.create_permission,
        ] + [self.action_permission(action) for action in self.get_actions()]

    async def has_view_perm(self, request: HttpRequest, *args, **kw) -> bool:
        user: AbstractUser = request.user
        return user.has_permission(self.view_permission)

    async def has_change_perm(self, request: HttpRequest, *args, **kw) -> bool:
        user: AbstractUser = request.user
        return user.has_permission(self.change_permission)

    async def has_delete_perm(self, request: HttpRequest, *args, **kw) -> bool:
        user: AbstractUser = request.user
        return user.has_permission(self.delete_permission)

    async def has_create_perm(self, request: HttpRequest, *args, **kw) -> bool:
        user: AbstractUser = request.user
        return user.has_permission(self.create_permission)

    async def has_action_perm(self, request: HttpRequest, *args, **kw) -> bool:
        body = await request.json()
        action = body.get("action", "")

        user: AbstractUser = request.user
        return user.has_permission(self.action_permission(action))
