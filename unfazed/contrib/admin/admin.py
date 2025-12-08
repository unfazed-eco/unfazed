from .registry import ModelAdmin, register
from .serializers import LogEntrySerializer


@register(LogEntrySerializer)
class LogEntryAdmin(ModelAdmin):
    datetime_fields = ["created_at"]
