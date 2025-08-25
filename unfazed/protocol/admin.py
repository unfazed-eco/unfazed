import typing as t


class AdminAuthProtocol(t.Protocol):
    @property
    def view_permission(self) -> str: ...

    @property
    def change_permission(self) -> str: ...

    @property
    def delete_permission(self) -> str: ...

    @property
    def create_permission(self) -> str: ...

    def action_permission(self, action: str) -> str: ...
