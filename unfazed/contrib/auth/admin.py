from unfazed.contrib.admin.registry import ModelAdmin, register

from .serializers import (
    GroupSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserSerializer,
)


@register(UserSerializer)
class UserAdmin(ModelAdmin):
    inlines = ["InlineGroupAdmin", "InlineRoleAdmin"]


@register(UserSerializer)
class InlineUserAdmin(ModelAdmin):
    pass


@register(GroupSerializer)
class GroupAdmin(ModelAdmin):
    inlines = ["InlineRoleAdmin", "InlineUserAdmin"]


@register(GroupSerializer)
class InlineGroupAdmin(ModelAdmin):
    pass


@register(RoleSerializer)
class RoleAdmin(ModelAdmin):
    inlines = ["PermissionAdmin"]


@register(RoleSerializer)
class InlineRoleAdmin(ModelAdmin):
    pass


@register(PermissionSerializer)
class PermissionAdmin(ModelAdmin):
    pass
