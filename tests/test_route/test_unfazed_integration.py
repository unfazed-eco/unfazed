import pytest

from unfazed.core import Unfazed
from unfazed.openapi.base import OpenApi
from unfazed.schema import OpenAPI as OpenAPISettingModel
from unfazed.test import Requestfactory


async def test_integration(setup_route_unfazed: Unfazed) -> None:
    routes = setup_route_unfazed.routes

    assert len(routes) == 7

    async with Requestfactory(setup_route_unfazed) as request:
        # test path
        response = await request.get("/path/foo")
        assert response.status_code == 200

        response = await request.get("/path/bar/subbar1")
        assert response.status_code == 200

        response = await request.get("/path/bar/subbar2")
        assert response.status_code == 200

        # test mount
        response = await request.get("/mount/app/bar")
        assert response.status_code == 200
        # test static html files
        response = await request.get("/static_html")
        assert response.status_code == 200
        # test static html files
        response = await request.get("/static/js/foo.js")
        assert response.status_code == 200

        response = await request.get("/static/css/bar.css")
        assert response.status_code == 200

        response = await request.get("/static/nested/top/sub/bar.js")
        assert response.status_code == 200

        response = await request.get("/static/index.html")
        assert response.status_code == 200

        with pytest.raises(FileNotFoundError):
            await request.get("/static/not_found.html")

        # test mount
        response = await request.get("/mount/app/bar")
        assert response.status_code == 200

        response = await request.get("/mount/route/bar")
        assert response.status_code == 200


async def test_openapi_integration(setup_route_unfazed: Unfazed) -> None:
    routes = setup_route_unfazed.routes

    OpenApi.create_schema(
        routes,
        OpenAPISettingModel.model_validate(
            {
                "openapi": "3.1.1",
                "info": {
                    "title": "test",
                    "description": "test",
                    "version": "1.0.0",
                },
                "allow_public": True,
            }
        ),
    )

    assert OpenApi.schema is not None
