# Petcare MCP Server

Starter Python MCP server for a petcare product. It exposes tool groups for:

- PostgreSQL reads and parameterized statements
- S3 uploads, downloads, object metadata, and presigned URLs
- external HTTP service calls behind an allowlist

This version is intentionally conservative:

- read-heavy by default
- parameterized SQL only
- external requests restricted to approved base URLs
- S3 access scoped to a configured bucket

## Structure

```text
petcare_mcp/
  config.py
  server.py
  tools/
    db.py
    s3.py
    external.py
```

## Setup

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

Stdio transport:

```bash
petcare-mcp
```

Streamable HTTP transport:

```bash
MCP_TRANSPORT=streamable-http petcare-mcp
```

## Suggested first tools for Petcare

- `db_query_select` for pet profiles, care plans, reminders, and audit reads
- `s3_create_presigned_upload_url` for profile photos and documents
- `external_fetch_json` for partner APIs like vet search or reminder providers

## Notes

- Keep business rules in your app and expose only the minimum safe operations here.
- If you later want petcare-specific tools, add wrapper tools such as `get_pet_profile`, `list_health_records`, or `create_care_reminder` on top of the generic DB layer.
