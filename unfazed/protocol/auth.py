import typing as t

from pydantic import BaseModel

from unfazed.type import Doc, GenericReponse


class BaseAuthBackend(t.Protocol):
    def __init__(self, options: t.Dict = {}) -> None: ...

    @property
    def alias(self) -> str: ...

    async def login(
        self, ctx: BaseModel
    ) -> t.Tuple[
        t.Annotated[
            t.Dict,
            Doc(description="session info, it will be set in the request.session"),
        ],
        t.Annotated[GenericReponse, Doc(description="response data")],
    ]: ...

    async def session_info(
        self, user: BaseModel, ctx: BaseModel
    ) -> t.Dict[str, t.Any]: ...

    async def register(self, ctx: BaseModel): ...
