from unfazed.exception.base import BaseUnfazedException


class ParameterError(BaseUnfazedException):
    def __init__(self, message: str = "Parameter Error", code: int = 401) -> None:
        self.message = message
        self.code = code
        super().__init__(message, code)
