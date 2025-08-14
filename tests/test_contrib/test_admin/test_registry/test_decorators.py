from tortoise import Model, fields

from unfazed.contrib.admin.registry import (
    ActionInput,
    ActionKwargs,
    ActionOutput,
    ModelAdmin,
    action,
    admin_collector,
    register,
)
from unfazed.serializer import Serializer


class Student(Model):
    name = fields.CharField(max_length=255)
    age = fields.IntField()


class StudenSerializer(Serializer):
    class Meta:
        model = Student


async def test_decorator() -> None:
    admin_collector.clear()

    @register(StudenSerializer)
    class StudentAdmin(ModelAdmin):
        @action(
            name="test_action",
            confirm=True,
            description="test_action",
            label="test_action",
            output=ActionOutput.Download,
            input=ActionInput.String,
            batch=True,
        )
        def test_action(self, ctx: ActionKwargs) -> str:
            return "test_action"

        @action(name="test_action2", confirm=True)
        async def test_action2(self, ctx: ActionKwargs) -> str:
            return "test_action2"

    assert "StudentAdmin" in admin_collector

    ins: ModelAdmin = admin_collector["StudentAdmin"]
    assert ins.serializer == StudenSerializer

    actions = ins.get_actions()

    assert "test_action" in actions

    action1 = actions["test_action"]
    assert action1.confirm is True
    assert action1.description == "test_action"
    assert action1.label == "test_action"
    assert action1.output == ActionOutput.Download
    assert action1.input == ActionInput.String
    assert action1.batch is True

    assert "test_action2" in actions

    assert getattr(ins, "test_action")() == "test_action"
    assert await getattr(ins, "test_action2")() == "test_action2"
