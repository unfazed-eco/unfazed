from unfazed.contrib.admin.registry import ModelAdmin, register
from unfazed.serializer import Serializer

from .models import User


class UserSerializer(Serializer):
    class Meta:
        model = User


@register(UserSerializer)
class UserAdmin(ModelAdmin):
    pass
