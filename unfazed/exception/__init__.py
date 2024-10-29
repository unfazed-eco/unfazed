from .route import ParameterError


class TypeHintRequired(Exception):
    pass


__all__ = ["TypeHintRequired", "ParameterError"]
