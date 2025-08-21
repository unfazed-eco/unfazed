from tortoise import Model, fields

from unfazed.contrib.common.base_models import JsonTextField


class BaseModel(Model):
    class Meta:
        abstract = True

    id = fields.IntField(primary_key=True)


class Article(BaseModel):
    title = fields.CharField(max_length=255)
    author = fields.CharField(max_length=255)
    content = fields.TextField()
    extra = JsonTextField(default={})


class Author(BaseModel):
    name = fields.CharField(max_length=255)
    age = fields.IntField()
