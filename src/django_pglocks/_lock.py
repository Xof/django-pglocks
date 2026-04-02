from __future__ import annotations

import hashlib
import inspect
from typing import Any


def resolve_lock_id(
    lock_id: str | int | tuple[int, int] | list[int],
) -> int | tuple[int, int]:
    """Normalize a lock ID to an int or (int, int) tuple."""
    if isinstance(lock_id, (list, tuple)):
        if len(lock_id) != 2:
            raise ValueError(
                "Tuples and lists as lock IDs must have exactly two entries."
            )
        if not isinstance(lock_id[0], int) or not isinstance(lock_id[1], int):
            raise ValueError("Both members of a tuple/list lock ID must be integers")
        return (lock_id[0], lock_id[1])

    if isinstance(lock_id, str):
        digest = hashlib.sha256(lock_id.encode("utf-8")).digest()[:8]
        return int.from_bytes(digest, byteorder="big", signed=True)

    if isinstance(lock_id, int):
        return lock_id

    raise ValueError(f"Cannot use {lock_id!r} as a lock id")


VALID_LOCK_FUNCTIONS = frozenset(
    {
        "pg_advisory_lock",
        "pg_advisory_lock_shared",
        "pg_try_advisory_lock",
        "pg_try_advisory_lock_shared",
        "pg_advisory_unlock",
        "pg_advisory_unlock_shared",
    }
)


def build_lock_sql(
    function_name: str,
    lock_id: int | tuple[int, int],
    comment: str,
) -> tuple[str, tuple[int, ...]]:
    """Build the SQL and parameters for a lock acquire/release call."""
    if function_name not in VALID_LOCK_FUNCTIONS:
        raise ValueError(f"Invalid lock function: {function_name}")

    params: tuple[int, ...]
    if isinstance(lock_id, tuple):
        sql = f"SELECT {function_name}(%s, %s) {comment}"
        params = (lock_id[0], lock_id[1])
    else:
        sql = f"SELECT {function_name}(%s) {comment}"
        params = (lock_id,)

    return sql, params


_SKIP_MODULES = frozenset({"django_pglocks", "contextlib"})


def build_comment(lock_id: Any) -> str:
    """Build an SQL comment with the lock ID and calling location."""
    frame_info = _find_caller_frame()
    if frame_info is None:
        return f"-- {lock_id!r}"
    filename, lineno = frame_info
    return f"-- {lock_id!r} @ {filename}:{lineno}"


def _find_caller_frame() -> tuple[str, int] | None:
    """Walk the stack to find the first frame outside django_pglocks and contextlib."""
    for frame_info in inspect.stack():
        module = frame_info.frame.f_globals.get("__name__", "")
        if not any(module.startswith(skip) for skip in _SKIP_MODULES):
            return frame_info.filename, frame_info.lineno
    return None


def resolve_comment_setting(comment: bool | None) -> bool:
    """Determine whether to add a comment based on the argument and Django settings."""
    if comment is not None:
        return comment

    from django.conf import settings

    advisory_setting = getattr(settings, "ADVISORY_LOCK_COMMENT", None)
    if advisory_setting is not None:
        return bool(advisory_setting)

    return bool(getattr(settings, "DEBUG", False))
