from unfazed.openapi.service import OpenApiService
from unfazed.schema import OpenAPI


def test_service():
    openapi_setting = OpenAPI(
        servers=[{"url": "http://localhost:8000", "description": "dev"}]
    )
    docs = OpenApiService._get_docs(
        title="project",
        openapi_url=openapi_setting.json_route,
        swagger_ui_css=openapi_setting.swagger_ui.css,
        swagger_ui_js=openapi_setting.swagger_ui.js,
        swagger_ui_favicon=openapi_setting.swagger_ui.favicon,
    )

    assert isinstance(docs, str)

    redoc = OpenApiService._get_redoc(
        title="project",
        redoc_spec=openapi_setting.json_route,
        redoc_js=openapi_setting.redoc.js,
    )

    assert isinstance(redoc, str)
