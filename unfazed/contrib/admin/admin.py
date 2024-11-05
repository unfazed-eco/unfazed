from .registry import ModelAdmin, register
from .serializers import LogEntrySerializer, MenuSerializer


@register(LogEntrySerializer)
class LogEntryAdmin(ModelAdmin):
    pass


@register(MenuSerializer)
class MenuAdmin(ModelAdmin):
    pass
