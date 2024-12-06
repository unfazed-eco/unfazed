from unfazed.serializer import Serializer

from .models import LogEntry


class LogEntrySerializer(Serializer):
    class Meta:
        model = LogEntry
