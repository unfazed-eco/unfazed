import typing as t

from tortoise import fields
from tortoise.fields.relational import ManyToManyRelation

from unfazed.conf import settings
from unfazed.contrib.common.base_models import (
    BaseModel,
    ForeignKeyField,
    ManyToManyField,
)
from unfazed.type import Doc
from unfazed.utils import import_string

from .settings import UnfazedContribAuthSettings


class AbstractUser(BaseModel):
    class Meta:
        abstract = True

    account = fields.CharField(max_length=255, default="", unique=True)
    password = fields.CharField(max_length=255, default="")
    email = fields.CharField(max_length=255, default="")
    is_superuser = fields.SmallIntField(default=0)

    groups: ManyToManyRelation["Group"]
    roles: ManyToManyRelation["Role"]

    @classmethod
    def UserCls(
        cls,
    ) -> t.Annotated[
        t.Type[t.Self],
        Doc(description="A model cls inherited from AbstractUser"),
    ]:
        auth_setting: UnfazedContribAuthSettings = settings[
            "UNFAZED_CONTRIB_AUTH_SETTINGS"
        ]
        user_cls = import_string(auth_setting.USER_MODEL)
        return user_cls

    async def query_roles(self) -> t.List["Role"]:
        await self.fetch_related("roles", "groups")

        ret = list(self.roles)
        for group in self.groups:
            roles_under_group = await group.query_roles()
            ret.extend(roles_under_group)

        return list(set(ret))

    async def query_groups(self) -> t.List["Group"]:
        await self.fetch_related("groups")
        return list(self.groups)

    async def has_permission(self, access: str) -> bool:
        if self.is_superuser:
            return True
        await self.fetch_related("roles", "groups")

        for role in self.roles:
            if await role.has_permission(access):
                return True

        for group in self.groups:
            await group.fetch_related("roles")
            for role in group.roles:
                if await role.has_permission(access):
                    return True

        return False

    @classmethod
    async def from_session(cls, session_dict: t.Dict[str, t.Any]) -> "AbstractUser":
        user_id = session_dict.get("id")
        return await cls.get(id=user_id)


class Group(BaseModel):
    class Meta:
        table = "unfazed_auth_group"

    name = fields.CharField(max_length=255)
    users = ManyToManyField(
        "models.User",
        through="models.UserGroup",
        forward_key="group_id",
        backward_key="user_id",
        related_name="groups",
    )

    roles: ManyToManyRelation["Role"]

    async def query_roles(self) -> t.List["Role"]:
        await self.fetch_related("roles")
        return list(self.roles)

    async def query_users(self) -> t.List["AbstractUser"]:
        await self.fetch_related("users")
        return list(self.users)


class UserGroup(BaseModel):
    class Meta:
        table = "unfazed_auth_user_group"

    user = ForeignKeyField(
        "models.User",
        related_name="user_groups",
        null=True,
    )

    group = ForeignKeyField(
        "models.Group",
        related_name="user_groups",
        null=True,
    )


class UserRole(BaseModel):
    class Meta:
        table = "unfazed_auth_user_role"

    user = ForeignKeyField(
        "models.User",
        related_name="user_roles",
        null=True,
    )

    role = ForeignKeyField(
        "models.Role",
        related_name="user_roles",
        null=True,
    )


class GroupRole(BaseModel):
    class Meta:
        table = "unfazed_auth_group_role"

    group = ForeignKeyField(
        "models.Group",
        related_name="group_roles",
        null=True,
    )

    role = ForeignKeyField(
        "models.Role",
        related_name="group_roles",
        null=True,
    )


class Role(BaseModel):
    class Meta:
        table = "unfazed_auth_role"

    name = fields.CharField(max_length=255)
    users = ManyToManyField(
        "models.User",
        through="models.UserRole",
        forward_key="role_id",
        backward_key="user_id",
        related_name="roles",
    )
    groups = ManyToManyField(
        "models.Group",
        through="models.GroupRole",
        forward_key="role_id",
        backward_key="group_id",
        related_name="roles",
    )
    permissions = ManyToManyField(
        "models.Permission",
        related_name="roles",
        on_delete=fields.NO_ACTION,
        db_constraint=False,
    )

    async def query_users(self) -> t.List["AbstractUser"]:
        await self.fetch_related("users", "groups")

        ret = list(self.users)
        for group in self.groups:
            users_under_group = await group.query_users()
            ret.extend(users_under_group)

        return list(set(ret))

    async def query_groups(self) -> t.List["Group"]:
        await self.fetch_related("groups")
        return list(self.groups)

    async def query_permissions(self) -> t.List["Permission"]:
        await self.fetch_related("permissions")
        return list(self.permissions)

    async def has_permission(self, access: str) -> bool:
        async for permission in self.query_permissions():
            if permission.access == access:
                return True

        return False


class RolePermission(BaseModel):
    class Meta:
        table = "unfazed_auth_role_permission"

    role = ForeignKeyField(
        "models.Role",
        related_name="role_permissions",
        null=True,
    )

    permission = ForeignKeyField(
        "models.Permission",
        related_name="role_permissions",
        null=True,
    )


class Permission(BaseModel):
    class Meta:
        table = "unfazed_auth_permission"

    access = fields.CharField(max_length=255)
    remark = fields.TextField(default="")

    roles: ManyToManyRelation["Role"]
