import typing as t
from enum import Enum

from tortoise import fields
from tortoise.models import Model

from unfazed.conf import settings
from unfazed.type import Doc
from unfazed.utils import import_string

from .settings import UnfazedContribAuthSettings


class Status(Enum):
    ACTIVE = 1
    INACTIVE = 0


class BaseModel(Model):
    class Meta:
        abstract = True

    id = fields.IntField(primary_key=True)
    created_at = fields.BigIntField()
    updated_at = fields.BigIntField()
    is_active = fields.SmallIntField(default=Status.ACTIVE, choices=Status)


class AbstractUser(BaseModel):
    class Meta:
        abstract = True

    account = fields.CharField(max_length=255, default="")
    password = fields.CharField(max_length=255, default="")
    email = fields.CharField(max_length=255, default="")
    is_superuser = fields.SmallIntField(default=0)

    @property
    def user(
        cls,
    ) -> t.Annotated[
        t.Type["AbstractUser"],
        Doc(description="A model cls inherited from AbstractUser"),
    ]:
        auth_setting: UnfazedContribAuthSettings = settings[
            "UNFAZED_CONTRIB_AUTH_SETTINGS"
        ]
        user_cls = import_string(auth_setting.AUTH_USER)
        return user_cls

    async def query_groups(cls) -> t.List["Group"]:
        pass

    async def bind_group(cls, group: "Group") -> None:
        pass

    async def bind_groups(cls, groups: t.List["Group"]) -> None:
        pass

    async def remove_groups(cls, groups: t.List["Group"]) -> None:
        pass

    async def clear_groups(cls) -> None:
        pass

    async def query_roles(cls) -> t.List["Role"]:
        pass

    async def bind_role(cls, role: "Role") -> None:
        pass

    async def bind_roles(cls, roles: t.List["Role"]) -> None:
        pass

    async def remove_roles(cls, roles: t.List["Role"]) -> None:
        pass

    async def clear_roles(cls) -> None:
        pass

    async def has_permission(cls, access: str) -> bool:
        pass


class Group(BaseModel):
    class Meta:
        table = "unfazed_auth_group"

    name = fields.CharField(max_length=255)
    users = fields.ManyToManyField(
        "models.User",
        related_name="groups",
        on_delete=fields.NO_ACTION,
        db_constraint=False,
    )

    async def query_users(cls) -> t.List["AbstractUser"]:
        pass

    async def bind_user(cls, user: "AbstractUser") -> None:
        pass

    async def bind_users(cls, users: t.List["AbstractUser"]) -> None:
        pass

    async def remove_users(cls, users: t.List["AbstractUser"]) -> None:
        pass

    async def clear_users(cls) -> None:
        pass

    async def query_roles(cls) -> t.List["Role"]:
        pass

    async def bind_role(cls, role: "Role") -> None:
        pass

    async def bind_roles(cls, roles: t.List["Role"]) -> None:
        pass

    async def remove_roles(cls, roles: t.List["Role"]) -> None:
        pass

    async def clear_roles(cls) -> None:
        pass


class Role(BaseModel):
    class Meta:
        table = "unfazed_auth_role"

    name = fields.CharField(max_length=255)
    users = fields.ManyToManyField(
        "models.User",
        related_name="roles",
        on_delete=fields.NO_ACTION,
        db_constraint=False,
    )
    groups = fields.ManyToManyField(
        "models.Group",
        related_name="roles",
        on_delete=fields.NO_ACTION,
        db_constraint=False,
    )
    permissions = fields.ManyToManyField(
        "models.Permission",
        related_name="roles",
        on_delete=fields.NO_ACTION,
        db_constraint=False,
    )

    async def query_users(cls) -> t.List["AbstractUser"]:
        pass

    async def bind_user(cls, user: "AbstractUser") -> None:
        pass

    async def bind_users(cls, users: t.List["AbstractUser"]) -> None:
        pass

    async def remove_users(cls, users: t.List["AbstractUser"]) -> None:
        pass

    async def clear_users(cls) -> None:
        pass

    async def query_groups(cls) -> t.List["Group"]:
        pass

    async def bind_group(cls, group: "Group") -> None:
        pass

    async def bind_groups(cls, groups: t.List["Group"]) -> None:
        pass

    async def remove_groups(cls, groups: t.List["Group"]) -> None:
        pass

    async def clear_groups(cls) -> None:
        pass

    async def query_permissions(cls) -> t.List["Permission"]:
        pass

    async def bind_permission(cls, permission: "Permission") -> None:
        pass

    async def bind_permissions(cls, permissions: t.List["Permission"]) -> None:
        pass

    async def remove_permissions(cls, permissions: t.List["Permission"]) -> None:
        pass

    async def clear_permissions(cls) -> None:
        pass


class Permission(BaseModel):
    class Meta:
        table = "unfazed_auth_permission"

    access = fields.CharField(max_length=255)
