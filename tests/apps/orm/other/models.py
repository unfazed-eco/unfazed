from tortoise import Model, fields


class Student2(Model):
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=100)
    age = fields.IntField()

    class Meta:
        table = "db_student2"
