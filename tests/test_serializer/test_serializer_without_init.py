from tests.apps.serializer.models import Student
from unfazed.serializer import Serializer


class StudentSerializer(Serializer):
    class Meta:
        model = Student
        enable_relations = True


class StudentSerializer2(Serializer):
    class Meta:
        model = Student
        enable_relations = False


async def test_serializer_without_init() -> None:
    fields = StudentSerializer.model_fields

    assert "id" in fields
    assert "name" in fields
    assert "age" in fields
    assert "courses" not in fields
    assert "bags" not in fields
    assert "profile" not in fields

    fields2 = StudentSerializer2.model_fields

    assert "id" in fields2
    assert "name" in fields2
    assert "age" in fields2
    assert "courses" not in fields2
    assert "bags" not in fields2
    assert "profile" not in fields2
