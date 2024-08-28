from unfazed.orm import tortoise as tt


class User(tt.Model):
    id = tt.IntField(primary_key=True)
    username = tt.CharField(max_length=255)
    email = tt.CharField(max_length=255)

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
