from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

import boto3
from botocore.client import BaseClient
from mcp.server.fastmcp import FastMCP

from petcare_mcp.config import Settings


@dataclass
class S3Client:
    bucket: str
    presign_expiry_seconds: int
    client: BaseClient

    def create_presigned_upload_url(self, key: str, content_type: str) -> dict[str, Any]:
        url = self.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=self.presign_expiry_seconds,
        )
        return {"bucket": self.bucket, "key": key, "method": "PUT", "url": url}

    def create_presigned_download_url(self, key: str) -> dict[str, Any]:
        url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=self.presign_expiry_seconds,
        )
        return {"bucket": self.bucket, "key": key, "method": "GET", "url": url}

    def get_object_metadata(self, key: str) -> dict[str, Any]:
        response = self.client.head_object(Bucket=self.bucket, Key=key)
        return {
            "bucket": self.bucket,
            "key": key,
            "content_length": response.get("ContentLength"),
            "content_type": response.get("ContentType"),
            "etag": response.get("ETag"),
            "last_modified": response.get("LastModified").isoformat() if response.get("LastModified") else None,
            "metadata": response.get("Metadata", {}),
        }

    def put_text_object(self, key: str, text: str, content_type: str = "text/plain; charset=utf-8") -> dict[str, Any]:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=text.encode("utf-8"), ContentType=content_type)
        return {"bucket": self.bucket, "key": key, "stored": True}

    def get_text_object(self, key: str, encoding: str = "utf-8") -> dict[str, Any]:
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        body = response["Body"].read().decode(encoding)
        return {"bucket": self.bucket, "key": key, "text": body}

    def put_base64_object(self, key: str, base64_data: str, content_type: str) -> dict[str, Any]:
        payload = base64.b64decode(base64_data)
        self.client.put_object(Bucket=self.bucket, Key=key, Body=payload, ContentType=content_type)
        return {"bucket": self.bucket, "key": key, "stored_bytes": len(payload)}


def register_s3_tools(mcp: FastMCP, s3: S3Client) -> None:
    @mcp.tool()
    def s3_create_presigned_upload_url(key: str, content_type: str) -> dict[str, Any]:
        """Create a presigned S3 upload URL for a file in the configured bucket."""
        return s3.create_presigned_upload_url(key, content_type)

    @mcp.tool()
    def s3_create_presigned_download_url(key: str) -> dict[str, Any]:
        """Create a presigned S3 download URL for a file in the configured bucket."""
        return s3.create_presigned_download_url(key)

    @mcp.tool()
    def s3_get_object_metadata(key: str) -> dict[str, Any]:
        """Read metadata for an object in the configured S3 bucket."""
        return s3.get_object_metadata(key)

    @mcp.tool()
    def s3_put_text_object(key: str, text: str, content_type: str = "text/plain; charset=utf-8") -> dict[str, Any]:
        """Store a text object in the configured S3 bucket."""
        return s3.put_text_object(key, text, content_type)

    @mcp.tool()
    def s3_get_text_object(key: str, encoding: str = "utf-8") -> dict[str, Any]:
        """Read a text object from the configured S3 bucket."""
        return s3.get_text_object(key, encoding)

    @mcp.tool()
    def s3_put_base64_object(key: str, base64_data: str, content_type: str) -> dict[str, Any]:
        """Store base64-decoded binary data as an object in the configured S3 bucket."""
        return s3.put_base64_object(key, base64_data, content_type)


def create_s3_client(settings: Settings) -> S3Client:
    session = boto3.session.Session(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        aws_session_token=settings.aws_session_token,
        region_name=settings.aws_region,
    )
    client = session.client("s3")
    return S3Client(
        bucket=settings.s3_bucket,
        presign_expiry_seconds=settings.s3_presign_expiry_seconds,
        client=client,
    )
