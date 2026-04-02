# django-pglocks 2.0 Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize django-pglocks to 2.0 with modern packaging, async support, full test coverage, and CI.

**Architecture:** Split the single-file library into focused modules (`_lock.py` for pure logic, `_sync.py` and `_async.py` for context managers) under a `src/` layout. TDD throughout, with unit tests for pure functions and integration tests against a real PostgreSQL database.

**Tech Stack:** Python 3.10+, Django 4.2+, hatchling (build), uv (dev), pytest + pytest-django + pytest-asyncio (test), ruff + mypy (lint), GitHub Actions (CI)

---

### Task 1: Project Scaffolding — Delete Old Files and Create Directory Structure

**Files:**
- Delete: `setup.py`, `MANIFEST`, `MANIFEST.in`, `CHANGES.txt`, `build/`, `dist/`, `django_pglocks.egg-info/`, `django_pglocks/models.py`, `django_pglocks/test_settings.py`, `django_pglocks/tests.py`, `django_pglocks/__init__.pyc`, `django_pglocks/__init__.py`
- Create: `src/django_pglocks/__init__.py` (placeholder), `src/django_pglocks/py.typed`
- Create: `tests/` directory
- Create: `pyproject.toml`
- Modify: `.gitignore`

- [ ] **Step 1: Delete old files and directories**

```bash
git rm setup.py MANIFEST MANIFEST.in CHANGES.txt
git rm -r build/ dist/ django_pglocks.egg-info/ django_pglocks/
rm -f django_pglocks/__init__.pyc
```

- [ ] **Step 2: Create new directory structure**

```bash
mkdir -p src/django_pglocks tests
```

- [ ] **Step 3: Create `pyproject.toml`**

Write `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "django-pglocks"
version = "2.0.0"
description = "Context managers for PostgreSQL advisory locks in Django."
readme = "README.rst"
license = "MIT"
requires-python = ">=3.10"
authors = [
    { name = "Christophe Pettus", email = "xof@thebuild.com" },
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Web Environment",
    "Framework :: Django",
    "Framework :: Django :: 4.2",
    "Framework :: Django :: 5.0",
    "Framework :: Django :: 5.1",
    "Framework :: Django :: 5.2",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development",
]
dependencies = [
    "django>=4.2",
]

[project.urls]
Homepage = "https://github.com/Xof/django-pglocks"
Repository = "https://github.com/Xof/django-pglocks"

[tool.hatch.build.targets.wheel]
packages = ["src/django_pglocks"]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "tests.django_settings"
pythonpath = ["src"]
asyncio_mode = "auto"

[tool.mypy]
python_version = "3.10"
strict = true
packages = ["django_pglocks"]
mypy_path = "src"

[tool.ruff]
src = ["src"]
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-django>=4.8",
    "pytest-asyncio>=0.23",
    "mypy>=1.10",
    "ruff>=0.5",
    "django-stubs>=5.0",
]
```

- [ ] **Step 4: Create placeholder `src/django_pglocks/__init__.py`**

Write `src/django_pglocks/__init__.py`:

```python
from importlib.metadata import version

__version__: str = version("django-pglocks")
```

- [ ] **Step 5: Create `src/django_pglocks/py.typed`**

Write `src/django_pglocks/py.typed` (empty file):

```
```

- [ ] **Step 6: Create test Django settings**

Write `tests/__init__.py` (empty file):

```
```

Write `tests/django_settings.py`:

```python
import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PGDATABASE", "django_pglocks"),
        "USER": os.environ.get("PGUSER", "django_pglocks"),
        "PASSWORD": os.environ.get("PGPASSWORD", "django_pglocks"),
        "HOST": os.environ.get("PGHOST", "localhost"),
        "PORT": os.environ.get("PGPORT", "5432"),
    },
}

INSTALLED_APPS: list[str] = []

SECRET_KEY = "test-secret-key-not-for-production"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

- [ ] **Step 7: Update `.gitignore`**

Write `.gitignore`:

```
# Python
*.py[cod]
__pycache__/
*.so
*.egg
*.egg-info/
dist/
build/
.eggs/

# Virtual environments
.venv/
venv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/
.mypy_cache/

# uv
uv.lock
```

- [ ] **Step 8: Run `uv sync` to verify packaging works**

```bash
uv sync
```

Expected: Dependencies install successfully, the package is installed in editable mode.

- [ ] **Step 9: Commit**

```bash
git add pyproject.toml src/ tests/__init__.py tests/django_settings.py .gitignore
git commit -m "Scaffold 2.0 project structure with pyproject.toml and src layout

Remove setup.py, distutils, six dependency, and build artifacts.
Switch to hatchling build backend with uv for development."
```

---

### Task 2: Core Internals — `_lock.py` with Unit Tests (TDD)

**Files:**
- Create: `src/django_pglocks/_lock.py`
- Create: `tests/test_lock_id.py`

- [ ] **Step 1: Write failing tests for `resolve_lock_id`**

Write `tests/test_lock_id.py`:

```python
from __future__ import annotations

import pytest

from django_pglocks._lock import resolve_lock_id


class TestResolveLockIdString:
    def test_string_returns_int(self) -> None:
        result = resolve_lock_id("test")
        assert isinstance(result, int)

    def test_string_is_deterministic(self) -> None:
        assert resolve_lock_id("hello") == resolve_lock_id("hello")

    def test_different_strings_differ(self) -> None:
        assert resolve_lock_id("foo") != resolve_lock_id("bar")

    def test_string_within_64_bit_range(self) -> None:
        result = resolve_lock_id("test")
        assert -(2**63) <= result <= 2**63 - 1

    def test_empty_string(self) -> None:
        result = resolve_lock_id("")
        assert isinstance(result, int)

    def test_long_string(self) -> None:
        result = resolve_lock_id("x" * 10000)
        assert isinstance(result, int)


class TestResolveLockIdInt:
    def test_int_passthrough(self) -> None:
        assert resolve_lock_id(42) == 42

    def test_negative_int(self) -> None:
        assert resolve_lock_id(-1) == -1

    def test_zero(self) -> None:
        assert resolve_lock_id(0) == 0

    def test_max_bigint(self) -> None:
        val = 2**63 - 1
        assert resolve_lock_id(val) == val

    def test_min_bigint(self) -> None:
        val = -(2**63)
        assert resolve_lock_id(val) == val


class TestResolveLockIdTuple:
    def test_tuple_passthrough(self) -> None:
        assert resolve_lock_id((5, 9)) == (5, 9)

    def test_list_normalized_to_tuple(self) -> None:
        assert resolve_lock_id([5, 9]) == (5, 9)

    def test_wrong_length_tuple(self) -> None:
        with pytest.raises(ValueError, match="exactly two"):
            resolve_lock_id((1,))

    def test_wrong_length_triple(self) -> None:
        with pytest.raises(ValueError, match="exactly two"):
            resolve_lock_id((1, 2, 3))

    def test_non_int_tuple_member(self) -> None:
        with pytest.raises(ValueError, match="integers"):
            resolve_lock_id((1, "a"))

    def test_empty_tuple(self) -> None:
        with pytest.raises(ValueError, match="exactly two"):
            resolve_lock_id(())


class TestResolveLockIdInvalid:
    def test_float_rejected(self) -> None:
        with pytest.raises(ValueError, match="Cannot use"):
            resolve_lock_id(3.14)  # type: ignore[arg-type]

    def test_none_rejected(self) -> None:
        with pytest.raises(ValueError, match="Cannot use"):
            resolve_lock_id(None)  # type: ignore[arg-type]

    def test_object_rejected(self) -> None:
        with pytest.raises(ValueError, match="Cannot use"):
            resolve_lock_id(object())  # type: ignore[arg-type]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_lock_id.py -v
```

Expected: ImportError — `_lock` module does not exist.

- [ ] **Step 3: Implement `resolve_lock_id`**

Write `src/django_pglocks/_lock.py`:

```python
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
            raise ValueError(
                "Both members of a tuple/list lock ID must be integers"
            )
        return (lock_id[0], lock_id[1])

    if isinstance(lock_id, str):
        digest = hashlib.sha256(lock_id.encode("utf-8")).digest()[:8]
        return int.from_bytes(digest, byteorder="big", signed=True)

    if isinstance(lock_id, int):
        return lock_id

    raise ValueError(f"Cannot use {lock_id!r} as a lock id")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_lock_id.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Write failing tests for `build_lock_sql`**

Append to `tests/test_lock_id.py`:

```python
from django_pglocks._lock import build_lock_sql


class TestBuildLockSql:
    def test_single_int_no_comment(self) -> None:
        sql, params = build_lock_sql("pg_advisory_lock", 42, "")
        assert sql == "SELECT pg_advisory_lock(%s) "
        assert params == (42,)

    def test_single_int_with_comment(self) -> None:
        sql, params = build_lock_sql("pg_advisory_lock", 42, "-- test comment")
        assert sql == "SELECT pg_advisory_lock(%s) -- test comment"
        assert params == (42,)

    def test_tuple_no_comment(self) -> None:
        sql, params = build_lock_sql("pg_advisory_lock", (5, 9), "")
        assert sql == "SELECT pg_advisory_lock(%s, %s) "
        assert params == (5, 9)

    def test_tuple_with_comment(self) -> None:
        sql, params = build_lock_sql(
            "pg_try_advisory_lock_shared", (5, 9), "-- locked"
        )
        assert sql == "SELECT pg_try_advisory_lock_shared(%s, %s) -- locked"
        assert params == (5, 9)
```

- [ ] **Step 6: Run tests to verify new tests fail**

```bash
uv run pytest tests/test_lock_id.py::TestBuildLockSql -v
```

Expected: ImportError — `build_lock_sql` not found.

- [ ] **Step 7: Implement `build_lock_sql`**

Append to `src/django_pglocks/_lock.py`:

```python
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

    if isinstance(lock_id, tuple):
        sql = f"SELECT {function_name}(%s, %s) {comment}"
        params = (lock_id[0], lock_id[1])
    else:
        sql = f"SELECT {function_name}(%s) {comment}"
        params = (lock_id,)

    return sql, params
```

- [ ] **Step 8: Run all tests to verify they pass**

```bash
uv run pytest tests/test_lock_id.py -v
```

Expected: All tests pass.

- [ ] **Step 9: Write failing tests for `build_comment`**

Append to `tests/test_lock_id.py`:

```python
from django_pglocks._lock import build_comment


class TestBuildComment:
    def test_returns_string(self) -> None:
        result = build_comment("my_lock")
        assert isinstance(result, str)

    def test_contains_lock_id_repr(self) -> None:
        result = build_comment("my_lock")
        assert "'my_lock'" in result

    def test_contains_filename(self) -> None:
        result = build_comment("my_lock")
        # This test file should be the caller
        assert "test_lock_id.py" in result

    def test_starts_with_sql_comment(self) -> None:
        result = build_comment("my_lock")
        assert result.startswith("-- ")

    def test_contains_line_number(self) -> None:
        result = build_comment(42)
        # Should contain "@ filename:NN" pattern
        assert " @ " in result

    def test_tuple_lock_id(self) -> None:
        result = build_comment((5, 9))
        assert "(5, 9)" in result
```

- [ ] **Step 10: Run tests to verify new tests fail**

```bash
uv run pytest tests/test_lock_id.py::TestBuildComment -v
```

Expected: ImportError — `build_comment` not found.

- [ ] **Step 11: Implement `build_comment`**

Append to `src/django_pglocks/_lock.py`:

```python
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
```

- [ ] **Step 12: Run all tests to verify they pass**

```bash
uv run pytest tests/test_lock_id.py -v
```

Expected: All tests pass.

- [ ] **Step 13: Write failing tests for `resolve_comment_setting`**

Append to `tests/test_lock_id.py`:

```python
from django_pglocks._lock import resolve_comment_setting


class TestResolveCommentSetting:
    def test_true_returns_true(self) -> None:
        assert resolve_comment_setting(True) is True

    def test_false_returns_false(self) -> None:
        assert resolve_comment_setting(False) is False

    def test_none_checks_advisory_lock_comment(self, settings: Any) -> None:
        settings.ADVISORY_LOCK_COMMENT = True
        assert resolve_comment_setting(None) is True

    def test_none_falls_back_to_debug(self, settings: Any) -> None:
        if hasattr(settings, "ADVISORY_LOCK_COMMENT"):
            del settings.ADVISORY_LOCK_COMMENT
        settings.DEBUG = True
        assert resolve_comment_setting(None) is True

    def test_none_defaults_false(self, settings: Any) -> None:
        if hasattr(settings, "ADVISORY_LOCK_COMMENT"):
            del settings.ADVISORY_LOCK_COMMENT
        settings.DEBUG = False
        assert resolve_comment_setting(None) is False
```

Also add at the top of `tests/test_lock_id.py`:

```python
from typing import Any
```

- [ ] **Step 14: Run tests to verify new tests fail**

```bash
uv run pytest tests/test_lock_id.py::TestResolveCommentSetting -v
```

Expected: ImportError — `resolve_comment_setting` not found.

- [ ] **Step 15: Implement `resolve_comment_setting`**

Append to `src/django_pglocks/_lock.py`:

```python
def resolve_comment_setting(comment: bool | None) -> bool:
    """Determine whether to add a comment based on the argument and Django settings."""
    if comment is not None:
        return comment

    from django.conf import settings

    advisory_setting = getattr(settings, "ADVISORY_LOCK_COMMENT", None)
    if advisory_setting is not None:
        return bool(advisory_setting)

    return bool(getattr(settings, "DEBUG", False))
```

- [ ] **Step 16: Run all `test_lock_id.py` tests**

```bash
uv run pytest tests/test_lock_id.py -v
```

Expected: All tests pass.

- [ ] **Step 17: Commit**

```bash
git add src/django_pglocks/_lock.py tests/test_lock_id.py
git commit -m "Add _lock.py with resolve_lock_id, build_lock_sql, build_comment, resolve_comment_setting

Pure functions for lock ID normalization (64-bit SHA-256 hashing for strings),
SQL assembly with parameterized queries, stack-walking comment builder, and
settings-aware comment toggle. Full unit test coverage."
```

---

### Task 3: Sync Context Manager — `_sync.py` with Tests (TDD)

**Files:**
- Create: `src/django_pglocks/_sync.py`
- Create: `tests/conftest.py`
- Create: `tests/test_sync.py`

- [ ] **Step 1: Create test fixtures in `conftest.py`**

Write `tests/conftest.py`:

```python
from __future__ import annotations

import pytest
from django.db import connections


@pytest.fixture
def db_cursor(db: None) -> None:
    """Marker fixture that ensures the test database is available.

    The `db` fixture from pytest-django handles database setup/teardown.
    """


@pytest.fixture
def second_connection(db: None):
    """Provide a second database connection for contention tests.

    Uses a raw psycopg connection so it has its own session, independent
    of Django's connection pooling.
    """
    conn_params = connections["default"].get_connection_params()
    engine = connections["default"].vendor  # "postgresql"
    raw_conn = connections["default"].Database.connect(
        **connections["default"].get_connection_params()
    )
    raw_conn.autocommit = True
    yield raw_conn
    raw_conn.close()
```

- [ ] **Step 2: Write failing tests for basic sync advisory lock**

Write `tests/test_sync.py`:

```python
from __future__ import annotations

import pytest
from django.db import DEFAULT_DB_ALIAS, connections

from django_pglocks import advisory_lock


def _check_advisory_lock_held(classid: int, objid: int) -> bool:
    """Check if an advisory lock is held by the current backend."""
    with connections[DEFAULT_DB_ALIAS].cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM pg_locks
            WHERE locktype = 'advisory'
              AND classid = %s
              AND objid = %s
              AND pid = pg_backend_pid()
            """,
            [classid, objid],
        )
        return cursor.fetchone() is not None


def _check_single_id_lock_held(lock_id: int) -> bool:
    """Check if a single-ID advisory lock is held by the current backend."""
    with connections[DEFAULT_DB_ALIAS].cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM pg_locks
            WHERE locktype = 'advisory'
              AND objid = %s
              AND pid = pg_backend_pid()
            """,
            [lock_id],
        )
        return cursor.fetchone() is not None


class TestSyncAdvisoryLockBasic:
    @pytest.mark.django_db
    def test_tuple_lock_acquired_and_released(self) -> None:
        with advisory_lock((5, 9)) as acquired:
            assert acquired is True
            assert _check_advisory_lock_held(5, 9)
        assert not _check_advisory_lock_held(5, 9)

    @pytest.mark.django_db
    def test_int_lock_acquired_and_released(self) -> None:
        with advisory_lock(123) as acquired:
            assert acquired is True
            assert _check_single_id_lock_held(123)
        assert not _check_single_id_lock_held(123)

    @pytest.mark.django_db
    def test_string_lock_acquired(self) -> None:
        with advisory_lock("test_lock") as acquired:
            assert acquired is True

    @pytest.mark.django_db
    def test_invalid_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Cannot use"):
            with advisory_lock(3.14):  # type: ignore[arg-type]
                pass


class TestSyncAdvisoryLockShared:
    @pytest.mark.django_db
    def test_shared_lock_acquired(self) -> None:
        with advisory_lock(123, shared=True) as acquired:
            assert acquired is True

    @pytest.mark.django_db
    def test_two_shared_locks(self, second_connection) -> None:
        """Two sessions can hold the same shared lock simultaneously."""
        with advisory_lock(999, shared=True) as acquired:
            assert acquired is True
            # Second connection also takes the shared lock
            cur = second_connection.cursor()
            cur.execute("SELECT pg_try_advisory_lock_shared(999)")
            second_acquired = cur.fetchone()[0]
            assert second_acquired is True
            cur.execute("SELECT pg_advisory_unlock_shared(999)")
            cur.close()


class TestSyncAdvisoryLockNoWait:
    @pytest.mark.django_db
    def test_nowait_acquires_when_free(self) -> None:
        with advisory_lock(456, wait=False) as acquired:
            assert acquired is True

    @pytest.mark.django_db
    def test_nowait_returns_false_when_held(self, second_connection) -> None:
        """wait=False returns False when another session holds the lock."""
        cur = second_connection.cursor()
        cur.execute("SELECT pg_advisory_lock(789)")
        cur.fetchone()
        try:
            with advisory_lock(789, wait=False) as acquired:
                assert acquired is False
        finally:
            cur.execute("SELECT pg_advisory_unlock(789)")
            cur.fetchone()
            cur.close()


class TestSyncAdvisoryLockComment:
    @pytest.mark.django_db
    def test_comment_true_adds_comment(self) -> None:
        """When comment=True, the SQL should contain a comment with the lock ID."""
        # We can't easily inspect the SQL after the fact, but we can verify
        # the lock still works with comments enabled.
        with advisory_lock((5, 9), comment=True) as acquired:
            assert acquired is True
        assert not _check_advisory_lock_held(5, 9)

    @pytest.mark.django_db
    def test_comment_false_overrides_debug(self, settings) -> None:
        settings.DEBUG = True
        with advisory_lock(123, comment=False) as acquired:
            assert acquired is True


class TestSyncAdvisoryLockExceptionSafety:
    @pytest.mark.django_db
    def test_lock_released_on_exception(self) -> None:
        with pytest.raises(RuntimeError, match="boom"):
            with advisory_lock((5, 9)) as acquired:
                assert acquired is True
                assert _check_advisory_lock_held(5, 9)
                raise RuntimeError("boom")
        assert not _check_advisory_lock_held(5, 9)
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
uv run pytest tests/test_sync.py -v
```

Expected: ImportError — `advisory_lock` cannot be imported from `django_pglocks`.

- [ ] **Step 4: Implement `_sync.py`**

Write `src/django_pglocks/_sync.py`:

```python
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
    """Context manager for PostgreSQL advisory locks (synchronous).

    Acquires an advisory lock on entry, releases it on exit.
    """
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
```

- [ ] **Step 5: Update `__init__.py` to export `advisory_lock`**

Replace `src/django_pglocks/__init__.py` with:

```python
from importlib.metadata import version

from django_pglocks._sync import advisory_lock

__all__ = ["advisory_lock"]
__version__: str = version("django-pglocks")
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
uv run pytest tests/test_sync.py -v
```

Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/django_pglocks/_sync.py src/django_pglocks/__init__.py tests/conftest.py tests/test_sync.py
git commit -m "Add sync advisory_lock context manager with integration tests

Keyword-only arguments, parameterized SQL, proper cursor lifecycle,
and full test coverage including shared locks, wait=False, comments,
and exception safety."
```

---

### Task 4: Async Context Manager — `_async.py` with Tests (TDD)

**Files:**
- Create: `src/django_pglocks/_async.py`
- Create: `tests/test_async.py`

- [ ] **Step 1: Write failing async tests**

Write `tests/test_async.py`:

```python
from __future__ import annotations

import pytest
from django.db import DEFAULT_DB_ALIAS, connections

from django_pglocks import async_advisory_lock


def _check_advisory_lock_held(classid: int, objid: int) -> bool:
    """Check if an advisory lock is held by the current backend."""
    with connections[DEFAULT_DB_ALIAS].cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM pg_locks
            WHERE locktype = 'advisory'
              AND classid = %s
              AND objid = %s
              AND pid = pg_backend_pid()
            """,
            [classid, objid],
        )
        return cursor.fetchone() is not None


def _check_single_id_lock_held(lock_id: int) -> bool:
    """Check if a single-ID advisory lock is held by the current backend."""
    with connections[DEFAULT_DB_ALIAS].cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM pg_locks
            WHERE locktype = 'advisory'
              AND objid = %s
              AND pid = pg_backend_pid()
            """,
            [lock_id],
        )
        return cursor.fetchone() is not None


class TestAsyncAdvisoryLockBasic:
    @pytest.mark.django_db(transaction=True)
    async def test_tuple_lock_acquired_and_released(self) -> None:
        async with async_advisory_lock((5, 9)) as acquired:
            assert acquired is True
            assert _check_advisory_lock_held(5, 9)
        assert not _check_advisory_lock_held(5, 9)

    @pytest.mark.django_db(transaction=True)
    async def test_int_lock_acquired_and_released(self) -> None:
        async with async_advisory_lock(123) as acquired:
            assert acquired is True
            assert _check_single_id_lock_held(123)
        assert not _check_single_id_lock_held(123)

    @pytest.mark.django_db(transaction=True)
    async def test_string_lock_acquired(self) -> None:
        async with async_advisory_lock("test_lock") as acquired:
            assert acquired is True

    @pytest.mark.django_db(transaction=True)
    async def test_invalid_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Cannot use"):
            async with async_advisory_lock(3.14):  # type: ignore[arg-type]
                pass


class TestAsyncAdvisoryLockShared:
    @pytest.mark.django_db(transaction=True)
    async def test_shared_lock_acquired(self) -> None:
        async with async_advisory_lock(123, shared=True) as acquired:
            assert acquired is True


class TestAsyncAdvisoryLockNoWait:
    @pytest.mark.django_db(transaction=True)
    async def test_nowait_acquires_when_free(self) -> None:
        async with async_advisory_lock(456, wait=False) as acquired:
            assert acquired is True

    @pytest.mark.django_db(transaction=True)
    async def test_nowait_returns_false_when_held(self, second_connection) -> None:
        cur = second_connection.cursor()
        cur.execute("SELECT pg_advisory_lock(789)")
        cur.fetchone()
        try:
            async with async_advisory_lock(789, wait=False) as acquired:
                assert acquired is False
        finally:
            cur.execute("SELECT pg_advisory_unlock(789)")
            cur.fetchone()
            cur.close()


class TestAsyncAdvisoryLockComment:
    @pytest.mark.django_db(transaction=True)
    async def test_comment_true_adds_comment(self) -> None:
        async with async_advisory_lock((5, 9), comment=True) as acquired:
            assert acquired is True
        assert not _check_advisory_lock_held(5, 9)


class TestAsyncAdvisoryLockExceptionSafety:
    @pytest.mark.django_db(transaction=True)
    async def test_lock_released_on_exception(self) -> None:
        with pytest.raises(RuntimeError, match="boom"):
            async with async_advisory_lock((5, 9)) as acquired:
                assert acquired is True
                assert _check_advisory_lock_held(5, 9)
                raise RuntimeError("boom")
        assert not _check_advisory_lock_held(5, 9)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_async.py -v
```

Expected: ImportError — `async_advisory_lock` cannot be imported.

- [ ] **Step 3: Implement `_async.py`**

Write `src/django_pglocks/_async.py`:

```python
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from django_pglocks._lock import (
    build_comment,
    build_lock_sql,
    resolve_comment_setting,
    resolve_lock_id,
)


@asynccontextmanager
async def async_advisory_lock(
    lock_id: str | int | tuple[int, int],
    *,
    shared: bool = False,
    wait: bool = True,
    comment: bool | None = None,
    using: str | None = None,
) -> AsyncGenerator[bool, None]:
    """Context manager for PostgreSQL advisory locks (asynchronous).

    Acquires an advisory lock on entry, releases it on exit.
    """
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
    async with connections[using].cursor() as cursor:
        await cursor.execute(sql, params)
        row = await cursor.fetchone()
        acquired = row[0]

    # Normalize: blocking variants return void/None in psycopg2.
    if wait:
        acquired = True

    try:
        yield acquired
    finally:
        if acquired:
            sql, params = build_lock_sql(
                release_function_name, resolved_id, comment_text
            )
            async with connections[using].cursor() as cursor:
                await cursor.execute(sql, params)
                await cursor.fetchone()
```

- [ ] **Step 4: Update `__init__.py` to export `async_advisory_lock`**

Replace `src/django_pglocks/__init__.py` with:

```python
from importlib.metadata import version

from django_pglocks._async import async_advisory_lock
from django_pglocks._sync import advisory_lock

__all__ = ["advisory_lock", "async_advisory_lock"]
__version__: str = version("django-pglocks")
```

- [ ] **Step 5: Run async tests**

```bash
uv run pytest tests/test_async.py -v
```

Expected: All tests pass.

- [ ] **Step 6: Run full test suite**

```bash
uv run pytest -v
```

Expected: All tests (unit + sync integration + async integration) pass.

- [ ] **Step 7: Commit**

```bash
git add src/django_pglocks/_async.py src/django_pglocks/__init__.py tests/test_async.py
git commit -m "Add async_advisory_lock context manager with integration tests

Uses Django's async cursor API. Mirrors sync version with shared internals.
Full test coverage including shared, wait=False, comments, and exception safety."
```

---

### Task 5: Docker Compose and Documentation

**Files:**
- Create: `docker-compose.yml`
- Create: `CHANGELOG.md`
- Modify: `README.rst`

- [ ] **Step 1: Create `docker-compose.yml`**

Write `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: django_pglocks
      POSTGRES_PASSWORD: django_pglocks
      POSTGRES_DB: django_pglocks
    ports:
      - "5432:5432"
    tmpfs:
      - /var/lib/postgresql/data
```

- [ ] **Step 2: Create `CHANGELOG.md`**

Write `CHANGELOG.md`:

```markdown
# Changelog

## 2.0.0 (unreleased)

### Breaking Changes

- **String lock IDs now hash to 64-bit values.** Previously used 32-bit CRC32; now uses SHA-256 truncated to 64 bits. Existing string-based lock IDs will resolve to different integer values.
- **Keyword-only arguments.** `shared`, `wait`, `comment`, and `using` must now be passed as keyword arguments: `advisory_lock("x", shared=True)` not `advisory_lock("x", True)`.
- **Minimum versions:** Python 3.10+, Django 4.2+.
- **Removed `six` dependency.**

### Added

- `async_advisory_lock` — async context manager using Django's async database API.
- Type annotations throughout, with `py.typed` marker (PEP 561).
- Full test suite with pytest (unit tests + sync/async integration tests).
- Docker Compose for contributor setup.
- GitHub Actions CI with Python/Django/PostgreSQL/psycopg matrix.

### Fixed

- SQL queries now use parameterized queries instead of string formatting.
- Cursor is properly closed if an exception occurs during lock acquisition.
- Stack frame inspection for comments now walks the stack dynamically instead of using a hardcoded frame index.
- Lock acquisition result is always consumed from the cursor.

### Changed

- Project uses `pyproject.toml` with hatchling build backend (replaces `setup.py`/`distutils`).
- Source moved to `src/` layout.

## 1.1

- Add optional comment to the lock acquire/release SELECT statement with the lock_id and calling point.

## 1.0.2

- Fixed bug where lock would not be released when acquired with `wait=False`.

## 1.0.1

- Removed transaction-level locks (behavior was surprising — lock persisted after context manager exit).

## 1.0

- Initial release.
```

- [ ] **Step 3: Update `README.rst`**

Write `README.rst`:

```rst
==============
django-pglocks
==============

django-pglocks provides context managers for PostgreSQL advisory locks in Django.

It requires Python 3.10+, Django 4.2+, PostgreSQL 14+, and psycopg2 or psycopg3.

Advisory Locks
==============

Advisory locks are application-level locks that are acquired and released purely by the client of the database; PostgreSQL never acquires them on its own. They are very useful as a way of signalling to other sessions that a higher-level resource than a single row is in use, without having to lock an entire table or some other structure.

It's entirely up to the application to correctly acquire the right lock.

Currently, the context managers only create session-level locks, as the behavior of a lock persisting after the context body has been exited is surprising, and there's no way of releasing a transaction-scope advisory lock except to exit the transaction.

Installing
==========

::

    pip install django-pglocks

Usage
=====

Synchronous
-----------

::

    from django_pglocks import advisory_lock

    with advisory_lock("my_lock") as acquired:
        # acquired is True; lock is held
        do_work()
    # lock is released

Asynchronous
------------

::

    from django_pglocks import async_advisory_lock

    async with async_advisory_lock("my_lock") as acquired:
        # acquired is True; lock is held
        await do_work()
    # lock is released

Parameters
----------

* ``lock_id`` -- The ID of the lock to acquire. It can be a string, integer, or a tuple of two integers. If it's a string, a SHA-256 hash is used to generate a 64-bit lock ID.

* ``shared`` (default False) -- If True, a shared lock is taken. Any number of sessions can hold a shared lock; an exclusive lock will wait until all shared locks are released.

* ``wait`` (default True) -- If True, the context manager waits until the lock is acquired (always yields True unless a deadlock occurs). If False, it returns immediately and yields False if the lock could not be acquired. The context body is always executed regardless.

* ``comment`` (default None) -- If True, an SQL comment is appended to the lock statements with the ``repr()`` of the ``lock_id`` and the calling location. If None, checks ``settings.ADVISORY_LOCK_COMMENT``, then ``settings.DEBUG``. Pass ``comment=False`` to override.

* ``using`` (default None) -- The database alias to use. If None, the default connection is used.

Development
===========

With local PostgreSQL::

    uv sync
    uv run pytest

With Docker Compose::

    docker compose up -d
    uv run pytest
    docker compose down

To create the test database (if not using Docker)::

    createuser -s -P django_pglocks
    createdb django_pglocks -O django_pglocks

License
=======

Released under the `MIT License <http://opensource.org/licenses/mit-license.php>`_.
```

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml CHANGELOG.md README.rst
git commit -m "Add Docker Compose, CHANGELOG.md, and updated README

Docker Compose provides a single PG container for contributors.
README documents both sync and async APIs, all parameters,
and local development workflows."
```

---

### Task 6: CI Pipeline — GitHub Actions

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create CI workflow**

```bash
mkdir -p .github/workflows
```

Write `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [master]
    tags: ["v*"]
  pull_request:
    branches: [master]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      - run: uv sync --frozen
      - run: uv run ruff check
      - run: uv run ruff format --check
      - run: uv run mypy

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      - run: uv build
      - run: ls -la dist/

  test-pr:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          # Oldest supported stack
          - python: "3.10"
            django: "4.2"
            postgres: "14"
            psycopg: "psycopg2-binary"
          # Newest supported stack
          - python: "3.13"
            django: "5.2"
            postgres: "17"
            psycopg: "psycopg[binary]"
          # Cross: old Python + new Django/PG + psycopg3
          - python: "3.10"
            django: "5.2"
            postgres: "17"
            psycopg: "psycopg[binary]"
          # Cross: new Python + old Django/PG + psycopg2
          - python: "3.13"
            django: "4.2"
            postgres: "14"
            psycopg: "psycopg2-binary"
          # Mid-range with psycopg3
          - python: "3.11"
            django: "5.0"
            postgres: "15"
            psycopg: "psycopg[binary]"
          # Mid-range with psycopg2
          - python: "3.12"
            django: "5.1"
            postgres: "16"
            psycopg: "psycopg2-binary"
          # psycopg3 with Django 4.2
          - python: "3.11"
            django: "4.2"
            postgres: "15"
            psycopg: "psycopg[binary]"
          # psycopg2 with Django 5.2
          - python: "3.12"
            django: "5.2"
            postgres: "16"
            psycopg: "psycopg2-binary"

    services:
      postgres:
        image: postgres:${{ matrix.postgres }}
        env:
          POSTGRES_USER: django_pglocks
          POSTGRES_PASSWORD: django_pglocks
          POSTGRES_DB: django_pglocks
        options: >-
          --health-cmd="pg_isready -U django_pglocks"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: uv sync --frozen
      - run: uv pip install 'django~=${{ matrix.django }}.0' '${{ matrix.psycopg }}'
      - run: uv run pytest -v
        env:
          PGHOST: localhost
          PGPORT: "5432"
          PGUSER: django_pglocks
          PGPASSWORD: django_pglocks
          PGDATABASE: django_pglocks

  test-full:
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python: ["3.10", "3.11", "3.12", "3.13"]
        django: ["4.2", "5.0", "5.1", "5.2"]
        postgres: ["14", "15", "16", "17"]
        psycopg: ["psycopg2-binary", "psycopg[binary]"]

    services:
      postgres:
        image: postgres:${{ matrix.postgres }}
        env:
          POSTGRES_USER: django_pglocks
          POSTGRES_PASSWORD: django_pglocks
          POSTGRES_DB: django_pglocks
        options: >-
          --health-cmd="pg_isready -U django_pglocks"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: uv sync --frozen
      - run: uv pip install 'django~=${{ matrix.django }}.0' '${{ matrix.psycopg }}'
      - run: uv run pytest -v
        env:
          PGHOST: localhost
          PGPORT: "5432"
          PGUSER: django_pglocks
          PGPASSWORD: django_pglocks
          PGDATABASE: django_pglocks
```

- [ ] **Step 2: Verify YAML syntax**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "Add GitHub Actions CI with tiered Django/Python/PG/psycopg matrix

PR builds run 8 corner-case combos. Pushes to master and tags run
the full 128-combo matrix. Separate lint, type-check, and build jobs."
```

---

### Task 7: Lint and Type-Check Cleanup

**Files:**
- Modify: `src/django_pglocks/_lock.py`, `src/django_pglocks/_sync.py`, `src/django_pglocks/_async.py`, `src/django_pglocks/__init__.py`

- [ ] **Step 1: Run ruff and fix any issues**

```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

Fix any issues reported.

- [ ] **Step 2: Run mypy and fix any issues**

```bash
uv run mypy
```

Fix type errors. Common fixes may include:
- Adding `type: ignore` comments for Django's dynamic `connections` object
- Ensuring all function signatures match across modules

- [ ] **Step 3: Run full test suite to confirm nothing broke**

```bash
uv run pytest -v
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add -u
git commit -m "Fix lint and type-check issues"
```

---

### Task 8: Final Cleanup — Remove Old Files from Git History

**Files:**
- Delete from git: `setup.py`, `MANIFEST`, `MANIFEST.in`, `CHANGES.txt`, `build/`, `dist/`, `django_pglocks.egg-info/`, `django_pglocks/`

This task handles the actual `git rm` of old files that were not yet removed (Task 1 creates the new structure; this task ensures the old files are gone from the working tree).

- [ ] **Step 1: Remove old files from git**

```bash
git rm -f setup.py MANIFEST MANIFEST.in CHANGES.txt 2>/dev/null || true
git rm -rf build/ dist/ django_pglocks.egg-info/ django_pglocks/ 2>/dev/null || true
```

- [ ] **Step 2: Verify only new structure remains**

```bash
git status
ls -R src/
ls -R tests/
```

Expected: Only the new `src/`, `tests/`, config files, and docs remain.

- [ ] **Step 3: Run full test suite**

```bash
uv run pytest -v
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Remove legacy files: setup.py, distutils artifacts, old django_pglocks/ directory"
```

---

### Task 9: Final Verification

- [ ] **Step 1: Verify the package builds**

```bash
uv build
ls -la dist/
```

Expected: `django_pglocks-2.0.0.tar.gz` and `django_pglocks-2.0.0-py3-none-any.whl` present.

- [ ] **Step 2: Verify the wheel contains the right files**

```bash
python3 -m zipfile -l dist/django_pglocks-2.0.0-py3-none-any.whl
```

Expected: Contains `django_pglocks/__init__.py`, `django_pglocks/_lock.py`, `django_pglocks/_sync.py`, `django_pglocks/_async.py`, `django_pglocks/py.typed`.

- [ ] **Step 3: Run full test suite one final time**

```bash
uv run pytest -v
```

Expected: All tests pass.

- [ ] **Step 4: Clean up build artifacts**

```bash
rm -rf dist/
```
