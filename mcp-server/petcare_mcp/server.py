from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from petcare_mcp.config import settings
from petcare_mcp.tools.db import create_db_client, register_db_tools
from petcare_mcp.tools.external import create_external_client, register_external_tools
from petcare_mcp.tools.s3 import create_s3_client, register_s3_tools


mcp = FastMCP("Petcare MCP Server", json_response=True)

register_db_tools(mcp, create_db_client(settings))
register_s3_tools(mcp, create_s3_client(settings))
register_external_tools(mcp, create_external_client(settings))


def main() -> None:
    transport = settings.mcp_transport
    if transport == "streamable-http":
        mcp.run(transport="streamable-http")
        return
    mcp.run()


if __name__ == "__main__":
    main()
