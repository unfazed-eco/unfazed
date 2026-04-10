import typing as t

from unfazed.contrib.admin.registry import admin_collector
from unfazed.contrib.admin.registry.schema import AdminBaseAttrs
from unfazed.contrib.admin.services import AdminModelService
from unfazed.http import HttpRequest


class _SuperUser:
    is_superuser = True


def build_request() -> HttpRequest:
    request = HttpRequest(scope={"type": "http", "method": "GET", "user": _SuperUser()})
    return request


def as_admin_attrs(desc: t.Any) -> AdminBaseAttrs:
    return t.cast(AdminBaseAttrs, desc.attrs)


async def test_log_entry_admin_attrs() -> None:
    if "LogEntryAdmin" not in admin_collector:
        __import__("unfazed.contrib.admin.admin")

    log_entry_desc = await AdminModelService.model_desc(
        "LogEntryAdmin", build_request()
    )
    log_entry_attrs = as_admin_attrs(log_entry_desc)

    assert log_entry_attrs.can_add is False
    assert log_entry_attrs.can_delete is False
    assert log_entry_attrs.can_edit is False
    assert log_entry_attrs.search_fields == [
        "path",
        "account",
        "created_at",
        "ip",
        "request",
        "response",
    ]
    assert log_entry_attrs.search_range_fields == ["created_at"]
