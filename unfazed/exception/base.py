class BaseUnfazedException(Exception):
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code
        super().__init__(message)
