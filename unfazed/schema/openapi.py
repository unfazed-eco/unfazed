import typing as t

from openapi_pydantic.v3.v3_1 import ExternalDocumentation, Info, Server
from pydantic import BaseModel, Field


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
    openapi: t.Literal["3.1.0", "3.1.1"] = "3.1.1"
    servers: t.List[Server] = [Server(url="/")]
    info: Info
    externalDocs: ExternalDocumentation | None = None

    # openapi ui config
    json_route: str = "/openapi/openapi.json"
    swagger_ui: SwaggerUI = SwaggerUI()
    redoc: Redoc = Redoc()

    # open to network
    allow_public: bool = Field(
        default=True,
        description="allow public access, set to False when deploy to production",
    )
