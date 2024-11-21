from unfazed.contrib.admin.registry import ModelAdmin, register, action

from .serializers import (
    GroupSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserSerializer,
)

# allow overriding
# UserAdmin and InlineUserAdmin


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

    @action(name="Update Permissions", batch=True)
    async def update_permissions(self, request, *args, **kw):
        pass

