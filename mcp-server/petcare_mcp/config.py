from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    mcp_transport: str = Field(default="stdio", alias="MCP_TRANSPORT")

    postgres_dsn: str = Field(alias="POSTGRES_DSN")
    postgres_max_rows: int = Field(default=100, alias="POSTGRES_MAX_ROWS")

    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    s3_bucket: str = Field(alias="S3_BUCKET")
    s3_presign_expiry_seconds: int = Field(default=3600, alias="S3_PRESIGN_EXPIRY_SECONDS")
    aws_access_key_id: str | None = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    aws_session_token: str | None = Field(default=None, alias="AWS_SESSION_TOKEN")

    allowed_external_base_urls: list[str] = Field(
        default_factory=list,
        alias="ALLOWED_EXTERNAL_BASE_URLS",
    )
    external_request_timeout_seconds: float = Field(
        default=20.0,
        alias="EXTERNAL_REQUEST_TIMEOUT_SECONDS",
    )
    external_auth_header_name: str | None = Field(default=None, alias="EXTERNAL_AUTH_HEADER_NAME")
    external_auth_header_value: str | None = Field(default=None, alias="EXTERNAL_AUTH_HEADER_VALUE")


settings = Settings()
