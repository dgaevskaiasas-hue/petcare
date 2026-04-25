from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp.server.fastmcp import FastMCP
from psycopg import AsyncConnection
from psycopg.rows import dict_row

from petcare_mcp.config import Settings


@dataclass
class DatabaseClient:
    dsn: str
    max_rows: int

    async def fetch_all(self, sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        async with await AsyncConnection.connect(self.dsn, row_factory=dict_row) as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params or [])
                rows = await cur.fetchmany(self.max_rows)
                return [dict(row) for row in rows]

    async def execute(self, sql: str, params: list[Any] | None = None) -> dict[str, Any]:
        async with await AsyncConnection.connect(self.dsn, row_factory=dict_row) as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params or [])
                await conn.commit()
                rowcount = cur.rowcount
                try:
                    rows = await cur.fetchall()
                except Exception:
                    rows = []
                return {
                    "rowcount": rowcount,
                    "rows": [dict(row) for row in rows[: self.max_rows]],
                }


def _ensure_single_statement(sql: str) -> None:
    statement = sql.strip().rstrip(";")
    if ";" in statement:
        raise ValueError("Only a single SQL statement is allowed.")


def _ensure_select_statement(sql: str) -> None:
    _ensure_single_statement(sql)
    if not sql.lstrip().lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed for this tool.")


def register_db_tools(mcp: FastMCP, db: DatabaseClient) -> None:
    @mcp.tool()
    async def db_query_select(sql: str, params: list[Any] | None = None) -> dict[str, Any]:
        """Run a parameterized SELECT query against the petcare database."""
        _ensure_select_statement(sql)
        rows = await db.fetch_all(sql, params)
        return {"count": len(rows), "rows": rows}

    @mcp.tool()
    async def db_execute_statement(sql: str, params: list[Any] | None = None) -> dict[str, Any]:
        """Run a single parameterized INSERT, UPDATE, or DELETE statement."""
        _ensure_single_statement(sql)
        lowered = sql.lstrip().lower()
        if lowered.startswith("select"):
            raise ValueError("Use db_query_select for SELECT statements.")
        return await db.execute(sql, params)


def create_db_client(settings: Settings) -> DatabaseClient:
    return DatabaseClient(dsn=settings.postgres_dsn, max_rows=settings.postgres_max_rows)
