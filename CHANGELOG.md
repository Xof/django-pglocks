# Changelog

## 2.1.0 (2026-04-04)

**Final release — this package has been consolidated into [django-pg-utils](https://github.com/Xof/django-pg-utils).**

This version is a compatibility shim that depends on `django-pg-utils` and re-exports
`advisory_lock` and `async_advisory_lock` with a deprecation warning. No further updates
will be made to this package.

## 2.0.0 (2026-04-02)

### Breaking Changes

- **String lock IDs now hash to 64-bit values.** Previously used 32-bit CRC32; now uses SHA-256 truncated to 64 bits. Existing string-based lock IDs will resolve to different integer values.
- **Keyword-only arguments.** `shared`, `wait`, `comment`, and `using` must now be passed as keyword arguments: `advisory_lock("x", shared=True)` not `advisory_lock("x", True)`.
- **Minimum versions:** Python 3.10+, Django 4.2+.
- **Removed `six` dependency.**

### Added

- `async_advisory_lock` — async context manager for advisory locks, using `asgiref.sync_to_async` to ensure acquire and release happen on the same PostgreSQL session.
- Type annotations throughout, with `py.typed` marker (PEP 561).
- Full test suite with pytest: 35 unit tests + 11 sync integration tests + 9 async integration tests.
- Docker Compose for contributor setup.
- GitHub Actions CI with Python 3.10-3.13 / Django 4.2-5.2 / PostgreSQL 14-17 / psycopg2+psycopg3 matrix (128 combinations on push, 8 on PRs).

### Fixed

- SQL queries now use parameterized queries instead of string formatting for lock IDs.
- Cursor is properly closed via try/finally if an exception occurs during lock acquisition.
- Stack frame inspection for comments now walks the stack dynamically instead of using a hardcoded frame index, making it resilient to internal refactoring.
- Lock acquisition result is always consumed from the cursor, even for blocking variants.

### Changed

- Project uses `pyproject.toml` with hatchling build backend (replaces `setup.py`/`distutils`).
- Source moved to `src/` layout.
- Internal logic split into `_lock.py` (pure functions), `_sync.py`, and `_async.py`.

## 1.1

- Add optional comment to the lock acquire/release SELECT statement with the lock_id and calling point.

## 1.0.2

- Fixed bug where lock would not be released when acquired with `wait=False`.

## 1.0.1

- Removed transaction-level locks (behavior was surprising — lock persisted after context manager exit).

## 1.0

- Initial release.
