from unfazed.exception.base import BaseUnfazedException


class ParameterError(BaseUnfazedException):
    def __init__(
        self, message: str = "Request Parameter Error", code: int = 401
    ) -> None:
        super().__init__(message, code)
