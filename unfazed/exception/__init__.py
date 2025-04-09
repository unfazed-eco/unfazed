from .auth import (
    AccountExisted,
    AccountNotFound,
    LoginRequired,
    PermissionDenied,
    WrongPassword,
)
from .base import BaseUnfazedException, UnfazedSetupError
from .http import MethodNotAllowed
from .route import ParameterError


class TypeHintRequired(Exception):
    pass


__all__ = [
    "TypeHintRequired",
    "ParameterError",
    "PermissionDenied",
    "BaseUnfazedException",
    "LoginRequired",
    "AccountNotFound",
    "WrongPassword",
    "AccountExisted",
    "MethodNotAllowed",
    "UnfazedSetupError",
]
