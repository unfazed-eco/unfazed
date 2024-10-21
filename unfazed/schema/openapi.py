import typing as t

from pydantic import BaseModel

from unfazed.type import Domain


class _Server(BaseModel):
    url: Domain
    description: str | None


class SwaggerUI(BaseModel):
    css: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
    js: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"
    favicon: str = (
        "https://www.openapis.org/wp-content/uploads/sites/3/2016/11/favicon.png"
    )


class Redoc(BaseModel):
    js: str = "https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"


class OpenAPI(BaseModel):
    servers: t.List[_Server]
    json_route: str = "/openapi/openapi.json"
    swagger_ui: SwaggerUI = SwaggerUI()
    redoc: Redoc = Redoc()
