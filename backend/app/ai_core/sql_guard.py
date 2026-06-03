"""SQL safety guardrail (pure standard library - no external deps).

This is the layer that sits between the LLM and your database: an AI can be
coaxed into emitting destructive SQL, so generated/queried statements are
validated here before they ever run.

Public API:
    quote_ident(name)        -> safely double-quote an identifier
    is_single_statement(sql) -> reject stacked queries
    assert_safe_select(sql)  -> raise unless sql is a single read-only query
    build_select(...)        -> build a parameterized SELECT from validated parts
"""
from __future__ import annotations

import re

_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Statement keywords that must never appear in a read-only query.
_FORBIDDEN = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "REPLACE", "MERGE", "CALL",
    "EXEC", "EXECUTE", "ATTACH", "PRAGMA", "VACUUM",
}


class UnsafeSQLError(ValueError):
    """Raised when SQL fails a safety check."""


def quote_ident(name: str) -> str:
    """Validate and double-quote an identifier (optionally schema-qualified)."""
    parts = name.split(".") if name else []
    if not parts or any(not _IDENT_RE.match(p) for p in parts):
        raise UnsafeSQLError(f"invalid identifier: {name!r}")
    return ".".join(f'"{p}"' for p in parts)


def _strip_quoted(sql: str) -> str:
    """Remove single- and double-quoted spans."""
    out: list[str] = []
    i, n = 0, len(sql)
    quote: str | None = None
    while i < n:
        c = sql[i]
        if quote:
            if c == quote:
                if i + 1 < n and sql[i + 1] == quote:
                    i += 2
                    continue
                quote = None
            i += 1
            continue
        if c in ("'", '"'):
            quote = c
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _statements(sql: str) -> list[str]:
    bare = _strip_quoted(sql)
    return [s.strip() for s in bare.split(";") if s.strip()]


def is_single_statement(sql: str) -> bool:
    return len(_statements(sql)) <= 1


def _has_comment(sql: str) -> bool:
    bare = _strip_quoted(sql)
    return "--" in bare or "/*" in bare


def assert_safe_select(sql: str) -> None:
    """Raise UnsafeSQLError unless sql is a single, read-only SELECT/WITH query."""
    if not sql or not sql.strip():
        raise UnsafeSQLError("empty SQL")
    if _has_comment(sql):
        raise UnsafeSQLError("SQL comments are not allowed")
    if not is_single_statement(sql):
        raise UnsafeSQLError("multiple statements are not allowed")

    bare = _strip_quoted(sql).strip()
    leading = re.match(r"[A-Za-z]+", bare)
    if not leading or leading.group(0).upper() not in {"SELECT", "WITH"}:
        raise UnsafeSQLError("only SELECT / WITH queries are allowed")

    tokens = {t.upper() for t in re.findall(r"[A-Za-z_]+", bare)}
    forbidden = tokens & _FORBIDDEN
    if forbidden:
        raise UnsafeSQLError(f"forbidden keyword(s): {', '.join(sorted(forbidden))}")


def build_select(
    table: str,
    columns: list[str],
    where: dict[str, object] | None = None,
) -> tuple[str, list[object]]:
    """Build a parameterized SELECT from validated identifiers."""
    if not columns:
        raise UnsafeSQLError("at least one column is required")

    tbl = quote_ident(table)
    cols = ", ".join(quote_ident(c) for c in columns)
    sql = f"SELECT {cols} FROM {tbl}"

    params: list[object] = []
    if where:
        clauses = []
        for col, val in where.items():
            clauses.append(f"{quote_ident(col)} = %s")
            params.append(val)
        sql += " WHERE " + " AND ".join(clauses)

    assert_safe_select(sql)  # defense in depth
    return sql, params
