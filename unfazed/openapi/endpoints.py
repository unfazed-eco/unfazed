import os

from jinja2 import Template

from unfazed.conf import settings
from unfazed.http import HttpRequest, HttpResponse, JsonResponse

from .base import OpenApi


async def redoc(request: HttpRequest) -> HttpResponse:
    unfazed_settings = settings.get("UNFAZED", {})
    context = {
        "title": unfazed_settings.get("PROJECT_NAME", "Unfazed"),
        "openapi_url": "/openapi/openapi.json",
    }

    html_path = os.path.join(os.path.dirname(__file__), "template/index.html")
    with open(html_path) as f:
        content = Template(f.read()).render(**context)
    return HttpResponse(content)


async def openapi_json(request: HttpRequest) -> JsonResponse:
    return JsonResponse(OpenApi.schema)
