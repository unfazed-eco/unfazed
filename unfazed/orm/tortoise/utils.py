from tortoise.models import Model


def model_to_dict(instance: Model) -> dict:
    """
    Convert a tortoise model instance to a dictionary.

    :param instance: The tortoise model instance to convert.
    """
    return instance.__dict__
