from tortoise import Model, fields


class User(Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    uid = fields.IntField()
    # sex = tt.IntField(default=0)
