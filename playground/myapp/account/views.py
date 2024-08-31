from unfazed.cache import caches
from unfazed.http import HttpRequest, HttpResponse, JsonResponse

from .models import User


async def list_user(request: HttpRequest) -> HttpResponse:
    cache = caches["default"]
    if await cache.has_key("users"):
        ret = cache.get("users")
    else:
        users = await User.list_user()
        cache.set("users", users, timeout=5)
        ret = users

    return JsonResponse({"users": ret or []})


async def create_user(request: HttpRequest) -> HttpResponse:
    username = request.query_params["username"]
    email = request.query_params["email"]

    user = await User.create_user(username, email)
    return JsonResponse({"id": user.id, "username": user.username, "email": user.email})
