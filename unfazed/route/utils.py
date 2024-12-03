import typing as t
import uuid


def generate_random_string() -> str:
    return uuid.uuid4().hex


def get_endpoint_name(endpoint: t.Callable) -> str:
    return endpoint.__name__
