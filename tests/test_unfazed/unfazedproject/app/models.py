from unfazed.orm.fields import Integer, String
from unfazed.orm.models import Meta, Model


class User(Model):
    first_name: str = String(max_length=50)
    last_name: str = String(max_length=50)
    age: int = Integer()

    meta: Meta = Meta(db_table="users")
