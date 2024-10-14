from .orm import SignalNotAllowed
from .route import ParameterError


class TypeHintRequired(Exception):
    pass


__all__ = ["SignalNotAllowed", "TypeHintRequired", "ParameterError"]
