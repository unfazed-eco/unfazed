from .auth import (
    AccountExisted,
    AccountNotFound,
    LoginRequired,
    PermissionDenied,
    WrongPassword,
)
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
    "AccountNotFound",
    "WrongPassword",
    "AccountExisted",
]
