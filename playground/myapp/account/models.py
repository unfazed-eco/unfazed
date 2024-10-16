from tortoise import Model, fields


class User(Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)

    class Meta:
        table = "account_user"

    @classmethod
    async def list_user(cls) -> list:
        users = await cls.all()

        return [
            {"id": user.id, "username": user.username, "email": user.email}
            for user in users
        ]

    @classmethod
    async def create_user(cls, username: str, email: str) -> "User":
        return await cls.create(username=username, email=email)
