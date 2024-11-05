from tortoise import Model, fields

from unfazed.contrib.admin.registry import ModelAdmin, register, admin_collector
from unfazed.db.tortoise.serializer import TSerializer

from unfazed.contrib.admin.services import AdminModelService

import pytest

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)


class Group(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)


class Role(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)


class UserSerializer(TSerializer):
    class Meta:
        model = User


class GroupSerializer(TSerializer):
    class Meta:
        model = Group


class RoleSerializer(TSerializer):
    class Meta:
        model = Role


@pytest.fixture()
def collector():

    admin_collector.clear()


    @register(GroupSerializer)
    class GroupAdmin(ModelAdmin):
        inlines = []


    @register(RoleSerializer)
    class RoleAdmin(ModelAdmin):
        inlines = []


    @register(UserSerializer)
    class UserAdmin(ModelAdmin):
        inlines = [GroupAdmin, RoleAdmin]

    yield admin_collector




async def test_route(collector) -> None:
    
    ret = AdminModelService.list_route()
