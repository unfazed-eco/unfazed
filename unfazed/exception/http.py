from .base import BaseUnfazedException


class MethodNotAllowed(BaseUnfazedException):
    def __init__(self, message: str = "Method not allowed", code: int = 405):
        self.message = message
        self.code = code
