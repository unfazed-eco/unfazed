from tortoise import Model, fields


class BaseModel(Model):
    class Meta:
        abstract = True

    id = fields.IntField(pk=True)


class Article(BaseModel):
    title = fields.CharField(max_length=255)
    author = fields.CharField(max_length=255)
    content = fields.TextField()
