import typing as t

from pydantic import BaseModel, Field


class Cors(BaseModel):
    """
    refer https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
    """

    allow_origins: t.List[str] = Field(
        default=["*"], description="List of allowed origins", alias="ALLOW_ORIGINS"
    )
    allow_methods: t.List[str] = Field(
        default=["*"], description="List of allowed methods", alias="ALLOW_METHODS"
    )
    allow_headers: t.List[str] = Field(
        default=[], description="List of allowed headers", alias="ALLOW_HEADERS"
    )
    allow_credentials: bool = Field(
        default=False, description="Allow credentials", alias="ALLOW_CREDENTIALS"
    )

    allow_origin_regex: str | None = Field(
        default=None, description="Allow origin regex", alias="ALLOW_ORIGIN_REGEX"
    )
    expose_headers: t.List[str] = Field(
        default=[], description="List of exposed headers", alias="EXPOSE_HEADERS"
    )
    max_age: int = Field(default=600, description="Max age", alias="MAX_AGE")


class TrustedHost(BaseModel):
    allowed_hosts: t.List[str] = Field(
        default=["*"], description="List of allowed hosts", alias="ALLOWED_HOSTS"
    )

    www_redirect: bool = Field(
        default=True, description="Redirect www to non-www", alias="WWW_REDIRECT"
    )


class GZip(BaseModel):
    minimum_size: int = Field(
        default=500, description="Minimum size for compression", alias="MINIMUM_SIZE"
    )

    compress_level: int = Field(
        default=9, description="Compression level", alias="COMPRESS_LEVEL"
    )
