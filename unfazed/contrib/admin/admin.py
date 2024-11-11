from .registry import ModelAdmin, register
from .serializers import LogEntrySerializer


@register(LogEntrySerializer)
class LogEntryAdmin(ModelAdmin):
    pass
