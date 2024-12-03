from unittest.mock import patch

from unfazed.core import Unfazed
from unfazed.openapi.service import OpenApiService
from unfazed.schema import OpenAPI
from unfazed.test import Requestfactory


def test_service() -> None:
    openapi_setting = OpenAPI.model_validate(
        {"servers": [{"url": "http://localhost:8000", "description": "dev"}]}
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


async def test_api(setup_openapi_unfazed: Unfazed) -> None:
    unfazed = setup_openapi_unfazed
    assert unfazed.settings.OPENAPI is not None

    with patch.object(OpenApiService, "get_settings", return_value=unfazed.settings):
        request = Requestfactory(unfazed)

        response = await request.get("/openapi/docs")
        assert response.status_code == 200

        response = await request.get("/openapi/redoc")
        assert response.status_code == 200

        response = await request.get("/openapi/openapi.json")
        assert response.status_code == 200
