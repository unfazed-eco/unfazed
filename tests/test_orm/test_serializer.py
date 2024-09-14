from tortoise import fields

from unfazed.orm.tortoise import Model
from unfazed.orm.tortoise.serializer import TSerializer


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)


class UserSerializer(TSerializer):
    class Meta:
        model = User


def test_user_serializer() -> None:
    user = UserSerializer

    breakpoint()
