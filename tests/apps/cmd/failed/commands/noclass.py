import typing as t


class Command:
    async def handle(self, **option: t.Any) -> str:
        return "should be raised"
