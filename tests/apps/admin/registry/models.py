import enum
import typing as t

from tortoise import Model
from tortoise import fields as f

from unfazed.contrib.common.base_models import (
    ForeignKeyField,
    ManyToManyField,
    OneToOneField,
)


class Brand(enum.StrEnum):
    BMW = "BMW"
    BENZ = "BENZ"


class Color(enum.IntEnum):
    RED = 1
    GREEN = 2


class Car(Model):
    id = f.BigIntField(primary_key=True)
    bits = f.BinaryField()
    limited = f.BooleanField()
    brand = f.CharEnumField(enum_type=Brand, default=Brand.BENZ)
    alias = f.CharField(max_length=100)
    year = f.DateField()
    production_datetime = f.DatetimeField(auto_now_add=True)
    release_datetime = f.DatetimeField()
    price = f.DecimalField(max_digits=10, decimal_places=2)
    length = f.FloatField()
    color = f.IntEnumField(enum_type=Color)
    height = f.IntField()
    extra_info: t.Dict = f.JSONField(default={})
    version = f.SmallIntField()
    description = f.TextField()
    usage = f.TimeDeltaField()
    late_used_time = f.TimeField()
    uuid = f.UUIDField()
    override = f.CharField(max_length=100)
    pic = f.CharField(max_length=255)
    created_at = f.BigIntField()

    class Meta:
        table = "test_models_car"


# inlines models for test
# use relation fields


class T1User(Model):
    id = f.BigIntField(primary_key=True)
    name = f.CharField(max_length=100)
    email = f.CharField(max_length=100)
    password = f.CharField(max_length=100)

    roles = ManyToManyField(
        "models.T1Role",
        related_name="users",
        through="test_models_t1_user_role",
        forward_key="role_id",
        backward_key="user_id",
    )

    class Meta:
        table = "test_models_t1_user"


class T1Role(Model):
    id = f.BigIntField(primary_key=True)
    name = f.CharField(max_length=100)

    class Meta:
        table = "test_models_t1_role"


class T1UserRole(Model):
    id = f.BigIntField(primary_key=True)
    user = ForeignKeyField("models.T1User", related_name="user_roles")
    role = ForeignKeyField("models.T1Role", related_name="user_roles")

    class Meta:
        table = "test_models_t1_user_role"


class T1Profile(Model):
    id = f.BigIntField(primary_key=True)
    user = OneToOneField("models.T1User", related_name="profile")

    class Meta:
        table = "test_models_t1_profile"


class T1Book(Model):
    id = f.BigIntField(primary_key=True)
    title = f.CharField(max_length=100)
    owner = ForeignKeyField("models.T1User", related_name="books")

    class Meta:
        table = "test_models_t1_book"


# inlines models for test
# do not use relation fields


class T2User(Model):
    id = f.BigIntField(primary_key=True)
    name = f.CharField(max_length=100)
    email = f.CharField(max_length=100)
    password = f.CharField(max_length=100)

    class Meta:
        table = "test_models_t2_user"


class T2Role(Model):
    id = f.BigIntField(primary_key=True)
    name = f.CharField(max_length=100)

    class Meta:
        table = "test_models_t2_role"


class T2UserRole(Model):
    id = f.BigIntField(primary_key=True)
    user_id = f.BigIntField()
    role_id = f.BigIntField()

    class Meta:
        table = "test_models_t2_user_role"


class T2Profile(Model):
    id = f.BigIntField(primary_key=True)
    user_id = f.BigIntField()

    class Meta:
        table = "test_models_t2_profile"


class T2Book(Model):
    id = f.BigIntField(primary_key=True)
    title = f.CharField(max_length=100)
    owner_id = f.BigIntField()

    class Meta:
        table = "test_models_t2_book"


# Models for testing nullable fields


class T3User(Model):
    id = f.BigIntField(primary_key=True)
    name = f.CharField(max_length=100)

    class Meta:
        table = "test_models_t3_user"


class T3Comment(Model):
    id = f.BigIntField(primary_key=True)
    content = f.TextField()
    # Nullable foreign key field
    user_id = f.BigIntField(null=True)

    class Meta:
        table = "test_models_t3_comment"


# Models for testing fk and o2o relations


class T4Author(Model):
    id = f.BigIntField(primary_key=True)
    name = f.CharField(max_length=100)

    class Meta:
        table = "test_models_t4_author"


class T4Post(Model):
    id = f.BigIntField(primary_key=True)
    title = f.CharField(max_length=200)
    author = ForeignKeyField("models.T4Author", related_name="posts")

    class Meta:
        table = "test_models_t4_post"


class T4AuthorProfile(Model):
    id = f.BigIntField(primary_key=True)
    bio = f.TextField()
    author = OneToOneField("models.T4Author", related_name="profile")

    class Meta:
        table = "test_models_t4_author_profile"
