import typing as t

from unfazed.contrib.auth.backends import BaseAuthBackend
from unfazed.contrib.auth.models import AbstractUser
from unfazed.contrib.auth.schema import LoginCtx, RegisterCtx
from unfazed.exception import AccountExisted, AccountNotFound, WrongPassword


class DefaultAuthBackend(BaseAuthBackend):
    @property
    def alias(self) -> str:
        return "default"

    async def login(self, ctx: LoginCtx) -> t.Tuple[t.Dict, t.Any]:
        # get user
        account, password = ctx.account, ctx.password
        UserCls: t.Type[AbstractUser] = AbstractUser.UserCls()

        has_account = await UserCls.filter(account=account)
        if not has_account:
            raise AccountNotFound(f"{account} not found")

        user = await UserCls.get_or_none(account=account, password=password)
        if not user:
            raise WrongPassword("Please Check your password")

        # build session info
        session_info = await self.session_info(user, ctx)

        # build response
        resp = session_info

        return session_info, resp

    async def register(self, ctx: RegisterCtx) -> t.Any:
        account, password = ctx.account, ctx.password
        email = ctx.extra.get("email", "")

        UserCls: t.Type[AbstractUser] = AbstractUser.UserCls()

        existed = await UserCls.filter(account=account)
        if existed:
            raise AccountExisted(f"account {account} has been registered")

        if not password:
            raise WrongPassword("password cannot be empty")

        await UserCls.create(account=account, password=password, email=email)

        return {}

    async def session_info(
        self, user: AbstractUser, ctx: LoginCtx
    ) -> t.Dict[str, t.Any]:
        session_info = {
            "id": user.id,
            "account": user.account,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "platform": ctx.platform,
        }

        return session_info

    async def logout(self, session: t.Dict[str, t.Any]) -> t.Any:
        return {}

    async def oauth_login_redirect(self) -> str:
        return ""

    async def oauth_logout_redirect(self) -> str:
        return ""
