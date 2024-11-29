import typing as t
from enum import Enum

from tortoise import fields
from tortoise.fields.relational import ManyToManyRelation
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
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.SmallIntField(default=Status.ACTIVE.value, choices=Status)


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
        t.Type["AbstractUser"],
        Doc(description="A model cls inherited from AbstractUser"),
    ]:
        auth_setting: UnfazedContribAuthSettings = settings[
            "UNFAZED_CONTRIB_AUTH_SETTINGS"
        ]
        user_cls = import_string(auth_setting.USER_MODEL)
        return user_cls

    async def query_roles(self):
        await self.fetch_related("roles", "groups")

        ret = list(self.roles)
        for group in self.groups:
            await group.fetch_related("roles")
            ret.extend(list(group.roles))

        return ret

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
    users = fields.ManyToManyField(
        "models.User",
        related_name="groups",
        on_delete=fields.NO_ACTION,
        db_constraint=False,
    )


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

    async def query_users(self) -> t.List["AbstractUser"]:
        await self.fetch_related("users", "groups")

        ret = list(self.users)
        for group in self.groups:
            await group.fetch_related("users")
            ret.extend(list(group.users))

        return ret

    async def has_permission(self, access: str) -> bool:
        await self.fetch_related("permissions")
        return any([p.access == access for p in self.permissions])


class Permission(BaseModel):
    class Meta:
        table = "unfazed_auth_permission"

    access = fields.CharField(max_length=255)
    remark = fields.TextField(default="")
