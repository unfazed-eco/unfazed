from tortoise import Model, fields


class BaseModel(Model):
    class Meta:
        abstract = True

    id = fields.IntField(pk=True)


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


class Role(BaseModel):
    class Meta:
        table = "test_unfazed_auth_role"

    name = fields.CharField(max_length=255)
    users = fields.ManyToManyField(
        "models.User",
        related_name="roles",
        on_delete=fields.NO_ACTION,
        db_constraint=False,
    )
    groups = fields.ManyToManyField(
        "models.Group",
        related_name="roles",
        on_delete=fields.NO_ACTION,
        db_constraint=False,
    )
