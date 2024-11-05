from .auth import LoginRequired, PermissionDenied
from .base import BaseUnfazedException
from .route import ParameterError


class TypeHintRequired(Exception):
    pass


__all__ = [
    "TypeHintRequired",
    "ParameterError",
    "PermissionDenied",
    "BaseUnfazedException",
    "LoginRequired",
]
