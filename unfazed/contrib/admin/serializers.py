from unfazed.serializer.tortoise import TSerializer

from .models import LogEntry


class LogEntrySerializer(TSerializer):
    class Meta:
        model = LogEntry
