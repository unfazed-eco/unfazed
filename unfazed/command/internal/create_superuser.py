import secrets
import string
import sys
import typing as t

from click import Option

from unfazed.command import BaseCommand
from unfazed.contrib.auth.models import AbstractUser


class Command(BaseCommand):
    name = "create-superuser"
    help_text = """Create a superuser

    Usage:

    >>> unfazed-cli create-superuser --email email@example.com
    """

    @t.override
    def add_arguments(self) -> t.List[Option]:
        return [
            Option(
                ["--email", "-e"],
                help="email of the superuser",
                type=str,
            ),
        ]

    async def handle(self, **options: t.Any) -> None:
        email: str = options["email"]
        UserCls: t.Type[AbstractUser] = AbstractUser.UserCls()

        user_obj: t.Optional[AbstractUser] = await UserCls.filter(email=email).first()
        if user_obj:
            sys.stdout.write(f"Superuser already exists: {email}\n")
            return

        rand_str = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(6)
        )
        await UserCls.create(
            email=email, account=email, is_superuser=1, password=rand_str
        )

        sys.stdout.write(f"Superuser created: {email} with password: {rand_str}\n")
