from unfazed.contrib.admin.registry import admin_collector


def test_admin_registry():
    assert "UserAdmin" in admin_collector
    assert "InlineUserAdmin" in admin_collector
    assert "GroupAdmin" in admin_collector
    assert "InlineGroupAdmin" in admin_collector
    assert "RoleAdmin" in admin_collector
    assert "InlineRoleAdmin" in admin_collector
    assert "PermissionAdmin" in admin_collector
