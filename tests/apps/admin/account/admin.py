from unfazed.contrib.admin.registry import ModelAdmin, register
from unfazed.db.tortoise.serializer import TSerializer

from .models import User

print("UserAdmin")


class UserSerializer(TSerializer):
    class Meta:
        model = User


@register(UserSerializer)
class UserAdmin(ModelAdmin):
    pass
