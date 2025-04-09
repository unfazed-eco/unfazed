class BaseUnfazedException(Exception):
    def __init__(self, message: str, code: int = -1):
        self.message = message
        self.code = code
        super().__init__(message)


class UnfazedSetupError(BaseUnfazedException):
    """
    Exception raised when the Unfazed framework fails to initialize.
    """

    pass
