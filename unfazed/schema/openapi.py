import typing as t

from pydantic import BaseModel

from unfazed.type import Domain


class Contact(BaseModel):
    name: t.Optional[str] = None
    url: t.Optional[str] = None
    email: t.Optional[str] = None


class License(BaseModel):
    name: str
    identifier: t.Optional[str] = None
    url: t.Optional[str] = None


class Info(BaseModel):
    title: str
    summary: t.Optional[str] = None
    description: t.Optional[str] = None
    termsOfService: t.Optional[str] = None
    contact: t.Optional[Contact] = None
    license: t.Optional[License] = None
    version: str | None = None


class Server(BaseModel):
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
    # openapi schema config
    servers: t.List[Server]
    info: Info
    jsonSchemaDialect: str | None = None

    # openapi ui config
    json_route: str = "/openapi/openapi.json"
    swagger_ui: SwaggerUI = SwaggerUI()
    redoc: Redoc = Redoc()
