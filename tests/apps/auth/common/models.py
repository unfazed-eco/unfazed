from tortoise import Model, fields

from unfazed.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Phone(Model):
    class Meta:
        table = "unfazed_auth_phone"

    name = fields.CharField(max_length=255)
