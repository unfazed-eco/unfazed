from unfazed.db.tortoise.serializer import TSerializer

from .models import Group, Role, User


class UserSerializer(TSerializer):
    class Meta:
        model = User


class GroupSerializer(TSerializer):
    class Meta:
        model = Group


class RoleSerializer(TSerializer):
    class Meta:
        model = Role
