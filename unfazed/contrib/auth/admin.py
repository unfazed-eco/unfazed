from unfazed.contrib.admin.registry import AdminRelation, ModelAdmin, register

from .serializers import (
    GroupSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserSerializer,
)


@register(UserSerializer)
class UserAdmin(ModelAdmin):
    inlines = [
        AdminRelation(target="InlineGroupAdmin"),
        AdminRelation(target="InlineRoleAdmin"),
    ]


@register(UserSerializer)
class InlineUserAdmin(ModelAdmin):
    pass


@register(GroupSerializer)
class GroupAdmin(ModelAdmin):
    inlines = [
        AdminRelation(target="InlineRoleAdmin"),
        AdminRelation(target="InlineUserAdmin"),
    ]


@register(GroupSerializer)
class InlineGroupAdmin(ModelAdmin):
    pass


@register(RoleSerializer)
class RoleAdmin(ModelAdmin):
    inlines = [AdminRelation(target="PermissionAdmin")]


@register(RoleSerializer)
class InlineRoleAdmin(ModelAdmin):
    pass


@register(PermissionSerializer)
class PermissionAdmin(ModelAdmin):
    pass
