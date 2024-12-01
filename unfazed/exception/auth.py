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


class AccountNotFound(BaseUnfazedException):
    def __init__(self, message: str = "Account Not Found", code: int = 404):
        self.message = message
        self.code = code
        super().__init__(message, code)


class WrongPassword(BaseUnfazedException):
    def __init__(self, message: str = "Wrong password", code: int = 405):
        self.message = message
        self.code = code
        super().__init__(message, code)


class AccountExisted(BaseUnfazedException):
    def __init__(self, message: str = "Account existed", code: int = 406):
        self.message = message
        self.code = code
        super().__init__(message, code)
