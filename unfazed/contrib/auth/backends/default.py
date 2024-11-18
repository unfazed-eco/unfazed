import typing as t

from tortoise import Model

from unfazed.contrib.auth.models import AbstractUser
from unfazed.contrib.auth.schema import LoginCtx, RegisterCtx
from unfazed.exception import AccountExisted, AccountNotFound, WrongPassword

from .base import BaseAuthBackend


class DefaultAuthBackend(BaseAuthBackend):
    @property
    def alias(self) -> str:
        return "default"

    # login
    async def login(self, ctx: LoginCtx) -> t.Tuple[t.Dict, t.Any]:
        # get user
        account, password = ctx.account, ctx.password
        UserCls: Model = AbstractUser.user

        has_account = await UserCls.filter(account=account)
        if not has_account:
            raise AccountNotFound(f"{account} not found")

        user = await UserCls.get_or_none(account=account, password=password)
        if not user:
            raise WrongPassword("Please Check your password")

        # build session info
        session_info = self.session_info(user, ctx)

        # build response
        resp = session_info

        return session_info, resp

    async def register(self, ctx: RegisterCtx) -> t.Any:
        account, password = ctx.account, ctx.password
        email = ctx.extra.get("email", "")

        UserCls: Model = AbstractUser.user

        existed = await UserCls.filter(account=account)
        if existed:
            raise AccountExisted(f"account {account} has been registered")

        if not password:
            raise WrongPassword("password cannot be empty")

        await UserCls.create(account=account, password=password, email=email)

        return {}
