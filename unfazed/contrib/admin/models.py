from tortoise import Model, fields


class LogEntry(Model):
    id = fields.IntField(pk=True)
    updated_at = fields.BigIntField()
    created_at = fields.BigIntField()
    account = fields.CharField(max_length=255)
    method = fields.CharField(max_length=255)
    path = fields.CharField(max_length=255)
    ip = fields.CharField(max_length=128)
    request = fields.TextField()
    response = fields.TextField()

    class Meta:
        table = "unfazed_admin_logentry"
        indexes = ("email",)


class Menu(Model):
    ROOT_ID = 0

    id = fields.IntField(pk=True)
    updated_at = fields.BigIntField()
    created_at = fields.BigIntField()
    name = fields.CharField(max_length=255)
    title = fields.CharField(max_length=255)
    access = fields.CharField(max_length=255)
    component = fields.CharField(max_length=255, default="")
    path = fields.CharField(max_length=255, default="")
    icon = fields.CharField(max_length=255, default="")
    pid = fields.IntegerField(default=ROOT_ID)
    weight = fields.IntegerField(default=1)

    class Meta:
        table = "unfazed_admin_menu"
