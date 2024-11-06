from tortoise import Model, fields

from unfazed.contrib.admin.registry import ModelAdmin, action, admin_collector, register
from unfazed.db.tortoise.serializer import TSerializer
from unfazed.http import HttpRequest


class Student(Model):
    name: str = fields.CharField(max_length=255)
    age: int = fields.IntField()


class StudentSerializer(TSerializer):
    class Meta:
        model = Student


async def test_decorator():
    admin_collector.clear()

    @register(StudentSerializer)
    class StudentAdmin(ModelAdmin):
        @action(name="test_action", confirm=True)
        def test_action(self, request: HttpRequest | None = None) -> str:
            return "test_action"

        @action(name="test_action2", confirm=True)
        async def test_action2(self, request: HttpRequest | None = None) -> str:
            return "test_action2"

        @property
        def name(self):
            return "StudentAdmin"

    assert "StudentAdmin" in admin_collector

    ins = admin_collector["StudentAdmin"]
    assert ins.serializer == StudentSerializer

    actions = ins.get_actions()

    assert "test_action" in actions
    assert "test_action2" in actions

    assert getattr(ins, "test_action")() == "test_action"
    assert await getattr(ins, "test_action2")() == "test_action2"
