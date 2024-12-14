import os
import typing as t

from jinja2 import Template

from unfazed.conf import UnfazedSettings, settings

from .base import OpenApi


class OpenApiService:
    @classmethod
    def get_settings(cls) -> UnfazedSettings:
        return settings["UNFAZED_SETTINGS"]  # pragma: no cover

    @classmethod
    def get_docs(cls) -> str:
        unfazed_setting: UnfazedSettings = cls.get_settings()

        openapi_setting = unfazed_setting.OPENAPI

        if not openapi_setting:
            raise ValueError("OpenAPI settings not found")

        return cls._get_docs(
            unfazed_setting.PROJECT_NAME or "Unfazed",
            openapi_setting.json_route,
            openapi_setting.swagger_ui.css,
            openapi_setting.swagger_ui.js,
            openapi_setting.swagger_ui.favicon,
        )

    @classmethod
    def _get_docs(
        cls,
        title: str,
        openapi_url: str,
        swagger_ui_css: str,
        swagger_ui_js: str,
        swagger_ui_favicon: str,
    ) -> str:
        context = {
            "title": title,
            "openapi_url": openapi_url,
            "swagger_ui_css": swagger_ui_css,
            "swagger_ui_js": swagger_ui_js,
            "swagger_ui_favicon": swagger_ui_favicon,
        }

        html_path = os.path.join(os.path.dirname(__file__), "template/swagger-ui.html")
        with open(html_path) as f:
            content = Template(f.read()).render(**context)
            return content

    @classmethod
    def build_openapi_json(cls) -> t.Dict[str, t.Any]:
        if not OpenApi.schema:
            raise ValueError("OpenAPI schema not found")  # pragma: no cover
        return OpenApi.schema

    @classmethod
    def get_redoc(cls) -> str:
        unfazed_setting: UnfazedSettings = cls.get_settings()

        openapi_setting = unfazed_setting.OPENAPI

        if not openapi_setting:
            raise ValueError("OpenAPI settings not found")

        return cls._get_redoc(
            unfazed_setting.PROJECT_NAME or "Unfazed",
            openapi_setting.json_route,
            openapi_setting.redoc.js,
        )

    @classmethod
    def _get_redoc(cls, title: str, redoc_spec: str, redoc_js: str) -> str:
        context = {"title": title, "redoc_spec": redoc_spec, "redoc_js": redoc_js}

        html_path = os.path.join(os.path.dirname(__file__), "template/redoc.html")
        with open(html_path) as f:
            content = Template(f.read()).render(**context)
            return content
