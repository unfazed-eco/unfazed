from unfazed.http import HtmlResponse, HttpRequest, JsonResponse

from .service import OpenApiService


def redoc(request: HttpRequest) -> HtmlResponse:
    content = OpenApiService.get_redoc()
    return HtmlResponse(content)


def docs(request: HttpRequest) -> HtmlResponse:
    content = OpenApiService.get_docs()
    return HtmlResponse(content)


def openapi_json(request: HttpRequest) -> JsonResponse:
    return JsonResponse(OpenApiService.build_openapi_json())
