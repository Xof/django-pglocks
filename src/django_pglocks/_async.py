from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from django_pglocks._lock import (
    build_comment,
    build_lock_sql,
    resolve_comment_setting,
    resolve_lock_id,
)


def _execute_lock_sql(using: str, sql: str, params: tuple[int, ...]) -> object:
    """Execute a lock SQL statement synchronously and return the first column.

    Intended to run inside a sync_to_async worker. Because thread_sensitive=True
    (the default), all calls from the same async task share the same thread and
    therefore the same Django connection — which is required for session-level
    advisory locks to be acquired and released on the same PostgreSQL session.
    """
    from django.db import connections

    with connections[using].cursor() as cursor:
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return row[0] if row is not None else None


def _close_connection(using: str) -> None:
    """Close the Django connection in the current (sync_to_async worker) thread."""
    from django.db import connections

    connections[using].close()


@asynccontextmanager
async def async_advisory_lock(
    lock_id: str | int | tuple[int, int],
    *,
    shared: bool = False,
    wait: bool = True,
    comment: bool | None = None,
    using: str | None = None,
) -> AsyncGenerator[bool, None]:
    """Context manager for PostgreSQL advisory locks (asynchronous)."""
    from asgiref.sync import sync_to_async
    from django.db import DEFAULT_DB_ALIAS

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

    acquire_sql, acquire_params = build_lock_sql(
        function_name, resolved_id, comment_text
    )
    release_sql, release_params = build_lock_sql(
        release_function_name, resolved_id, comment_text
    )

    # Acquire. With thread_sensitive=True (default), all sync_to_async calls
    # from the same coroutine share one thread and one Django connection, which
    # ensures the advisory lock acquire and release happen on the same session.
    result = await sync_to_async(_execute_lock_sql)(using, acquire_sql, acquire_params)

    # Normalize: blocking variants return void/None in psycopg2.
    if wait:
        acquired: bool = True
    else:
        acquired = bool(result)

    try:
        yield acquired
    finally:
        if acquired:
            await sync_to_async(_execute_lock_sql)(using, release_sql, release_params)
        # Always close the worker thread's connection to avoid leaving open sessions.
        await sync_to_async(_close_connection)(using)
