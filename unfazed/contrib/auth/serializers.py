from unfazed.serializer.tortoise import TSerializer

from .models import AbstractUser, Group, Permission, Role


class GroupSerializer(TSerializer):
    class Meta:
        model = Group


class RoleSerializer(TSerializer):
    class Meta:
        model = Role


class PermissionSerializer(TSerializer):
    class Meta:
        model = Permission


class UserSerializer(TSerializer):
    class Meta:
        model = AbstractUser.UserCls()
