from tortoise import Model, fields


class LogEntry(Model):
    id = fields.IntField(primary_key=True)
    created_at = fields.BigIntField()
    account = fields.CharField(max_length=255)
    path = fields.CharField(max_length=255)
    ip = fields.CharField(max_length=128)
    request = fields.TextField()
    response = fields.TextField()

    class Meta:
        table = "unfazed_admin_logentry"
        indexes = ("account",)
