from unfazed.serializer import Serializer

from . import models as m


class GroupSerializer(Serializer):
    class Meta:
        model = m.Group


class RoleSerializer(Serializer):
    class Meta:
        model = m.Role


class PermissionSerializer(Serializer):
    class Meta:
        model = m.Permission


class UserSerializer(Serializer):
    class Meta:
        model = m.AbstractUser.UserCls()


class UserGroupSerializer(Serializer):
    class Meta:
        model = m.UserGroup


class UserRoleSerializer(Serializer):
    class Meta:
        model = m.UserRole


class GroupRoleSerializer(Serializer):
    class Meta:
        model = m.GroupRole


class RolePermissionSerializer(Serializer):
    class Meta:
        model = m.RolePermission
