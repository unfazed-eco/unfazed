from unfazed.serializer import Serializer

from .models import AbstractUser, Group, Permission, Role


class GroupSerializer(Serializer):
    class Meta:
        model = Group


class RoleSerializer(Serializer):
    class Meta:
        model = Role


class PermissionSerializer(Serializer):
    class Meta:
        model = Permission


class UserSerializer(Serializer):
    class Meta:
        model = AbstractUser.UserCls()
