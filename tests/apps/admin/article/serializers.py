from unfazed.db.tortoise.serializer import TSerializer

from .models import Choice, Question


class QuestionSerializer(TSerializer):
    class Meta:
        model = Question


class ChoiceSerializer(TSerializer):
    class Meta:
        model = Choice
