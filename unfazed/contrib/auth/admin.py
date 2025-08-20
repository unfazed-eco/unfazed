from unfazed.contrib.admin.registry import (
    AdminRelation,
    ModelAdmin,
    ModelInlineAdmin,
    register,
)

from .mixin import AuthMixin
from .serializers import (
    GroupSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserSerializer,
)


@register(UserSerializer)
class UserAdmin(ModelAdmin, AuthMixin):
    inlines = [
        AdminRelation(target="InlineGroupAdmin"),
        AdminRelation(target="InlineRoleAdmin"),
    ]


@register(UserSerializer)
class InlineUserAdmin(ModelInlineAdmin):
    pass


@register(GroupSerializer)
class GroupAdmin(ModelAdmin, AuthMixin):
    inlines = [
        AdminRelation(target="InlineRoleAdmin"),
        AdminRelation(target="InlineUserAdmin"),
    ]


@register(GroupSerializer)
class InlineGroupAdmin(ModelInlineAdmin):
    pass


@register(RoleSerializer)
class RoleAdmin(ModelAdmin, AuthMixin):
    inlines = [AdminRelation(target="PermissionAdmin")]


@register(RoleSerializer)
class InlineRoleAdmin(ModelInlineAdmin):
    pass


@register(PermissionSerializer)
class PermissionAdmin(ModelInlineAdmin):
    pass
