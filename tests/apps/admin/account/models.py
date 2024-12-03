from tortoise import Model, fields


class BaseModel(Model):
    class Meta:
        abstract = True

    id = fields.IntField(primary_key=True)


class User(BaseModel):
    name = fields.CharField(max_length=255)
    age = fields.IntField()

    class Meta:
        table = "test_unfazed_auth_user"


class Group(BaseModel):
    class Meta:
        table = "test_unfazed_auth_group"

    name = fields.CharField(max_length=255)
    users = fields.ManyToManyField(
        "models.User",
        related_name="groups",
        on_delete=fields.NO_ACTION,
        db_constraint=False,
    )


class Profile(BaseModel):
    class Meta:
        table = "test_unfazed_auth_profile"

    user: fields.OneToOneRelation = fields.OneToOneField(
        "models.User",
        related_name="profile",
        on_delete=fields.NO_ACTION,
        db_constraint=False,
    )
    avatar = fields.CharField(max_length=255)


class Book(BaseModel):
    class Meta:
        table = "test_unfazed_auth_book"

    title = fields.CharField(max_length=255)
    author = fields.CharField(max_length=255)
    owner: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User",
        related_name="books",
        on_delete=fields.NO_ACTION,
        db_constraint=False,
    )
