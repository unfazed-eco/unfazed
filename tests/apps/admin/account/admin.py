from unfazed.contrib.admin.registry import ModelAdmin, register
from unfazed.serializer.tortoise import TSerializer

from .models import User


class UserSerializer(TSerializer):
    class Meta:
        model = User


@register(UserSerializer)
class UserAdmin(ModelAdmin):
    pass
