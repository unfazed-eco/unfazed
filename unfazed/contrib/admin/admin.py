from .registry import ModelAdmin, register
from .serializers import LogEntrySerializer


@register(LogEntrySerializer)
class LogEntryAdmin(ModelAdmin):
    datetime_fields = ["created_at"]
    can_delete = False
    can_add = False
    can_edit = False

    search_fields = ["path", "account", "created_at", "ip", "request", "response"]
    search_range_fields = ["created_at"]
