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

    username = fields.CharField(max_length=255, default="")
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


class Permission(BaseModel):
    class Meta:
        table = "unfazed_auth_permission"

    access = fields.CharField(max_length=255)
