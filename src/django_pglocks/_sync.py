from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from django_pglocks._lock import (
    build_comment,
    build_lock_sql,
    resolve_comment_setting,
    resolve_lock_id,
)


@contextmanager
def advisory_lock(
    lock_id: str | int | tuple[int, int],
    *,
    shared: bool = False,
    wait: bool = True,
    comment: bool | None = None,
    using: str | None = None,
) -> Generator[bool, None, None]:
    """Context manager for PostgreSQL advisory locks (synchronous)."""
    from django.db import DEFAULT_DB_ALIAS, connections

    if using is None:
        using = DEFAULT_DB_ALIAS

    resolved_id = resolve_lock_id(lock_id)

    # Build function names.
    function_name = "pg_"
    if not wait:
        function_name += "try_"
    function_name += "advisory_lock"
    if shared:
        function_name += "_shared"

    release_function_name = "pg_advisory_unlock"
    if shared:
        release_function_name += "_shared"

    # Build comment.
    add_comment = resolve_comment_setting(comment)
    comment_text = build_comment(lock_id) if add_comment else ""

    # Acquire.
    sql, params = build_lock_sql(function_name, resolved_id, comment_text)
    cursor = connections[using].cursor()
    try:
        cursor.execute(sql, params)
        acquired = cursor.fetchone()[0]
    finally:
        cursor.close()

    # For the blocking variants, pg_advisory_lock returns void (None in
    # psycopg2, but True in psycopg3). Normalize to True.
    if wait:
        acquired = True

    try:
        yield acquired
    finally:
        if acquired:
            sql, params = build_lock_sql(
                release_function_name, resolved_id, comment_text
            )
            cursor = connections[using].cursor()
            try:
                cursor.execute(sql, params)
                cursor.fetchone()
            finally:
                cursor.close()
