from unfazed.db.tortoise.serializer import TSerializer

from .models import LogEntry


class LogEntrySerializer(TSerializer):
    class Meta:
        model = LogEntry
