from tortoise import Model, fields

from unfazed.contrib.admin.registry import ModelAdmin, action, admin_collector, register
from unfazed.db.tortoise.serializer import TSerializer
from unfazed.http import HttpRequest


class User(Model):
    name: str = fields.CharField(max_length=255)
    age: int = fields.IntField()


class UserSerializer(TSerializer):
    class Meta:
        model = User


async def test_decorator():
    admin_collector.clear()

    @register(UserSerializer)
    class UserAdmin(ModelAdmin):
        @action(name="test_action", confirm=True)
        def test_action(self, request: HttpRequest | None = None) -> str:
            return "test_action"

        @action(name="test_action2", confirm=True)
        async def test_action2(self, request: HttpRequest | None = None) -> str:
            return "test_action2"

        @property
        def name(self):
            return "UserAdmin"

    assert "UserAdmin" in admin_collector

    ins = admin_collector["UserAdmin"]
    assert ins.serializer == UserSerializer

    actions = ins.get_actions()

    assert "test_action" in actions
    assert "test_action2" in actions

    assert getattr(ins, "test_action")() == "test_action"
    assert await getattr(ins, "test_action2")() == "test_action2"
