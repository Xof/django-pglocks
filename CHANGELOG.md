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
