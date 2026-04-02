# django-pglocks Modernization Design

## Overview

Modernize django-pglocks from its 2013-era packaging and code to a well-maintained, modern Python library. This is a 2.0 release with breaking changes.

## Goals

- Modern packaging with `pyproject.toml` and `uv`
- Full test coverage with pytest
- Async support via a new `async_advisory_lock` context manager
- CI pipeline with Django/Python/PostgreSQL/psycopg matrix
- Code quality fixes (SQL parameterization, 64-bit hashing, robust stack inspection)
- Type annotations throughout

## Supported Versions

- Python: 3.10, 3.11, 3.12, 3.13
- Django: 4.2, 5.0, 5.1, 5.2
- PostgreSQL: 14, 15, 16, 17
- psycopg: psycopg2, psycopg3

## Project Structure

```
django-pglocks/
├── pyproject.toml
├── README.rst
├── LICENSE.txt
├── CHANGELOG.md
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── django_pglocks/
│       ├── __init__.py       # public API re-exports, dynamic __version__
│       ├── _lock.py          # shared internals (ID hashing, SQL assembly, comments)
│       ├── _sync.py          # sync context manager
│       ├── _async.py         # async context manager
│       └── py.typed          # PEP 561 marker
├── tests/
│   ├── conftest.py           # pytest/Django config, fixtures
│   ├── test_lock_id.py       # unit tests (no DB)
│   ├── test_sync.py          # sync integration tests
│   └── test_async.py         # async integration tests
└── .gitignore
```

### Files Deleted

- `setup.py` (replaced by `pyproject.toml`)
- `MANIFEST`, `MANIFEST.in` (not needed with modern build)
- `CHANGES.txt` (replaced by `CHANGELOG.md`)
- `build/`, `dist/`, `django_pglocks.egg-info/` (build artifacts, should never have been committed)
- `django_pglocks/models.py` (empty)
- `django_pglocks/test_settings.py` (replaced by `tests/conftest.py`)
- `django_pglocks/tests.py` (replaced by `tests/`)
- `django_pglocks/__init__.pyc` (bytecode)
- `docs/` (empty directory, recreated with actual content)

## Packaging

- Build backend: hatchling
- Version defined in `pyproject.toml` only
- `__version__` read dynamically via `importlib.metadata`
- Dependencies: `django >= 4.2`
- No `six` dependency
- Python requires: `>= 3.10`
- `src/` layout

## Internal Architecture

### `_lock.py` — Shared Internals

Pure functions, no database access.

- `resolve_lock_id(lock_id: str | int | tuple[int, int] | list[int]) -> int | tuple[int, int]`
  - Strings: SHA-256 hash truncated to 64-bit signed integer (breaking change from 32-bit crc32)
  - Tuples/lists: validated as length-2 integer pairs; lists normalized to tuples
  - Ints: passed through
  - All other types: `ValueError`

Note: Django's async cursor API is available from Django 4.1+, which is within our 4.2 floor.

- `build_lock_sql(function_name: str, lock_id: int | tuple[int, int], comment: str) -> tuple[str, tuple[...]]`
  - Returns `(sql_template, params)` for use with `cursor.execute(sql, params)`
  - Function name inserted via string formatting (from a fixed known set)
  - Lock IDs passed as query parameters

- `build_comment(lock_id: Any, skip_modules: set[str]) -> str`
  - Walks the stack to find the first frame outside of `django_pglocks` and `contextlib`
  - Returns `-- repr(lock_id) @ filename:lineno` or empty string

- `resolve_comment_setting(comment: bool | None) -> bool`
  - `True`/`False`: use as given
  - `None`: check `settings.ADVISORY_LOCK_COMMENT`, then `settings.DEBUG`

### `_sync.py` — Sync Context Manager

```python
@contextmanager
def advisory_lock(
    lock_id: str | int | tuple[int, int],
    *,
    shared: bool = False,
    wait: bool = True,
    comment: bool | None = None,
    using: str | None = None,
) -> Generator[bool, None, None]:
```

- Uses `connections[using].cursor()` with proper `with` / try-finally
- Always consumes `fetchone()` result regardless of `wait` value
- `shared`, `wait`, `comment`, `using` are keyword-only (breaking change)

### `_async.py` — Async Context Manager

```python
@asynccontextmanager
async def async_advisory_lock(
    lock_id: str | int | tuple[int, int],
    *,
    shared: bool = False,
    wait: bool = True,
    comment: bool | None = None,
    using: str | None = None,
) -> AsyncGenerator[bool, None]:
```

- Uses Django's async cursor API
- Same logic as sync, same parameter validation via shared `_lock.py`

### `__init__.py` — Public API

```python
from importlib.metadata import version

from django_pglocks._sync import advisory_lock
from django_pglocks._async import async_advisory_lock

__version__: str = version("django-pglocks")
```

## Breaking Changes (1.x -> 2.0)

1. **String lock IDs hash differently.** Moved from 32-bit crc32 to 64-bit SHA-256 truncation. Any code relying on specific hash values for string lock IDs will see different lock IDs.
2. **Keyword-only arguments.** `shared`, `wait`, `comment`, `using` must be passed as keyword arguments.
3. **Python 2 dropped.** (Already not functional, but now explicit.)
4. **Django < 4.2 dropped.**
5. **`six` dependency removed.**

## Code Quality Fixes

### SQL Parameter Handling

Current code uses Python `%` string formatting for lock IDs in SQL. New code passes lock IDs as query parameters via `cursor.execute(sql, params)`. Function names remain string-formatted since they are constructed from a fixed internal set.

### 64-bit String Hashing

Current `crc32` produces 32-bit values, wasting half the advisory lock ID space. New code uses `hashlib.sha256` → first 8 bytes → `int.from_bytes(..., signed=True)` for deterministic 64-bit IDs.

### Robust Stack Frame Inspection

Current code uses hardcoded `stack()[2][0]`. New code walks the stack looking for the first frame whose module is not `django_pglocks` or `contextlib`, making it resilient to internal refactoring or contextlib implementation changes.

### Cursor Lifecycle

All cursor usage wrapped in try/finally to ensure cleanup on exceptions during acquire.

### Result Consumption

Always call `fetchone()` after executing the lock SQL, even for blocking variants, to fully consume the result.

## Test Strategy

### Framework

pytest + pytest-django + pytest-asyncio

### `test_lock_id.py` — Unit Tests (No Database)

- String hashing: deterministic, 64-bit signed int, consistent across calls
- Tuple validation: length-2 int pairs required
- Int passthrough
- Invalid types rejected (float, None, objects, etc.)
- Edge cases: empty string, long strings, negative ints, boundary values (2^63-1, -2^63)

### `test_sync.py` — Sync Integration Tests

- Basic acquire/release: lock visible in `pg_locks`, gone after context exit
- String lock ID: acquires successfully
- Tuple lock ID: correct `classid`/`objid` in `pg_locks`
- `shared=True`: two connections hold the same shared lock
- `wait=False`: returns `False` when held, `True` when available
- `comment=True`: comment visible in `pg_stat_activity`
- `comment=False`: overrides settings
- Exception in body: lock still released
- `using=` parameter: non-default alias
- Invalid lock ID types: raises `ValueError`

### `test_async.py` — Async Integration Tests

Mirror of sync tests using `async with async_advisory_lock(...)`.

### `conftest.py`

- Django settings configuration (env vars with defaults for localhost:5432)
- Second database connection fixture for contention tests

## Local Development

### With Local PostgreSQL

```bash
uv sync
uv run pytest
```

### With Docker Compose (Contributors)

```bash
docker compose up -d
uv run pytest
docker compose down
```

### `docker-compose.yml`

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
```

Test settings read `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` from environment with defaults matching the Docker Compose config.

## CI Pipeline

### GitHub Actions (`.github/workflows/ci.yml`)

#### Tiered Matrix

**Full matrix (pushes to `main`, release tags):** All combinations:
- Python: 3.10, 3.11, 3.12, 3.13
- Django: 4.2, 5.0, 5.1, 5.2
- PostgreSQL: 14, 15, 16, 17
- psycopg: psycopg2-binary, psycopg[binary]
- 128 combinations total

**Reduced matrix (PRs):** ~8-10 corner cases:
- Python 3.10 + Django 4.2 + PG 14 + psycopg2
- Python 3.13 + Django 5.2 + PG 17 + psycopg3
- Python 3.12 + Django 5.1 + PG 16 + psycopg2
- Python 3.10 + Django 5.2 + PG 17 + psycopg2
- Python 3.13 + Django 4.2 + PG 14 + psycopg3
- Plus a few more edge combos

**PostgreSQL:** GitHub Actions `services:` with `postgres:XX` Docker images.

#### Additional CI Jobs (Run Once, Not Per Matrix Entry)

- **Lint + format:** `ruff check` + `ruff format --check`
- **Type check:** `mypy`
- **Build check:** `uv build` produces valid sdist and wheel
