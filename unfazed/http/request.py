import orjson as json
from starlette.requests import Request as StarletteRequest


class Request(StarletteRequest):
    async def json(self):
        # replace the default json method with orjson
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = json.loads(body)
        return self._json
