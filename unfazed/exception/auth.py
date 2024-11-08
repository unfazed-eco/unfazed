from .base import BaseUnfazedException


class PermissionDenied(BaseUnfazedException):
    def __init__(self, message: str = "Permission Denied", code: int = 403):
        self.message = message
        self.code = code
        super().__init__(message, code)


class LoginRequired(BaseUnfazedException):
    def __init__(self, message: str = "Login Required", code: int = 401):
        self.message = message
        self.code = code
        super().__init__(message, code)
