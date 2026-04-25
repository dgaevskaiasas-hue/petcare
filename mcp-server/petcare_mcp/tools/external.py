from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from mcp.server.fastmcp import FastMCP

from petcare_mcp.config import Settings


@dataclass
class ExternalServiceClient:
    allowed_base_urls: list[str]
    timeout_seconds: float
    auth_header_name: str | None
    auth_header_value: str | None

    def _normalize_base(self, base_url: str) -> str:
        return base_url.rstrip("/") + "/"

    def _build_headers(self, extra_headers: dict[str, str] | None) -> dict[str, str]:
        headers = dict(extra_headers or {})
        if self.auth_header_name and self.auth_header_value and self.auth_header_name not in headers:
            headers[self.auth_header_name] = self.auth_header_value
        return headers

    def _validate_url(self, base_url: str, path: str) -> str:
        normalized_base = self._normalize_base(base_url)
        if normalized_base not in [self._normalize_base(url) for url in self.allowed_base_urls]:
            raise ValueError("Base URL is not in the allowed external service list.")
        full_url = urljoin(normalized_base, path.lstrip("/"))
        if not full_url.startswith(normalized_base):
            raise ValueError("Path escapes the allowed base URL.")
        parsed = urlparse(full_url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only http and https URLs are allowed.")
        return full_url

    async def fetch_json(
        self,
        base_url: str,
        path: str,
        method: str = "GET",
        query: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = self._validate_url(base_url, path)
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.request(
                method=method.upper(),
                url=url,
                params=query,
                json=json_body,
                headers=self._build_headers(headers),
            )
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "url": str(response.url),
                "data": response.json(),
            }

    async def fetch_text(
        self,
        base_url: str,
        path: str,
        method: str = "GET",
        query: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = self._validate_url(base_url, path)
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.request(
                method=method.upper(),
                url=url,
                params=query,
                headers=self._build_headers(headers),
            )
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "url": str(response.url),
                "text": response.text,
            }


def register_external_tools(mcp: FastMCP, external: ExternalServiceClient) -> None:
    @mcp.tool()
    async def external_fetch_json(
        base_url: str,
        path: str,
        method: str = "GET",
        query: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Call an approved external JSON API."""
        return await external.fetch_json(base_url, path, method, query, json_body, headers)

    @mcp.tool()
    async def external_fetch_text(
        base_url: str,
        path: str,
        method: str = "GET",
        query: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Call an approved external HTTP endpoint and return text."""
        return await external.fetch_text(base_url, path, method, query, headers)


def create_external_client(settings: Settings) -> ExternalServiceClient:
    return ExternalServiceClient(
        allowed_base_urls=settings.allowed_external_base_urls,
        timeout_seconds=settings.external_request_timeout_seconds,
        auth_header_name=settings.external_auth_header_name,
        auth_header_value=settings.external_auth_header_value,
    )
