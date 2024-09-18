from .orm import SignalNotAllowed


class TypeHintRequired(Exception):
    pass


__all__ = ["SignalNotAllowed", "TypeHintRequired"]
