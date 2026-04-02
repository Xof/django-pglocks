# django-pglocks

django-pglocks provides context managers for PostgreSQL advisory locks in Django.

It requires Python 3.10+, Django 4.2+, PostgreSQL 14+, and psycopg2 or psycopg3.

## Advisory Locks

Advisory locks are application-level locks that are acquired and released purely by the client of the database; PostgreSQL never acquires them on its own. They are very useful as a way of signalling to other sessions that a higher-level resource than a single row is in use, without having to lock an entire table or some other structure.

It's entirely up to the application to correctly acquire the right lock.

Currently, the context managers only create session-level locks, as the behavior of a lock persisting after the context body has been exited is surprising, and there's no way of releasing a transaction-scope advisory lock except to exit the transaction.

## Installing

```
pip install django-pglocks
```

**Important:** django-pglocks requires a PostgreSQL database adapter — either [psycopg2](https://pypi.org/project/psycopg2/) or [psycopg3](https://pypi.org/project/psycopg/) — but does not install one automatically. You must install one yourself. Since Django itself needs one to talk to PostgreSQL, you almost certainly already have one installed.

## Usage

### Synchronous

```python
from django_pglocks import advisory_lock

with advisory_lock("my_lock") as acquired:
    # acquired is True; lock is held
    do_work()
# lock is released
```

### Asynchronous

```python
from django_pglocks import async_advisory_lock

async with async_advisory_lock("my_lock") as acquired:
    # acquired is True; lock is held
    await do_work()
# lock is released
```

### Parameters

Both `advisory_lock` and `async_advisory_lock` accept the same parameters. All parameters other than `lock_id` are keyword-only.

- **`lock_id`** — The ID of the lock to acquire. It can be:
  - A **string**: a SHA-256-based hash is used to generate a 64-bit lock ID.
  - An **integer**: used directly as the lock ID.
  - A **tuple of two integers**: used as the two-argument form of PostgreSQL's advisory lock functions (`classid`, `objid`).

- **`shared`** (default `False`) — If `True`, a shared lock is taken. Any number of sessions can hold a shared lock simultaneously; an exclusive lock will wait until all shared locks are released.

- **`wait`** (default `True`) — If `True`, the context manager waits until the lock is acquired, and always yields `True` (unless a deadlock occurs, in which case PostgreSQL raises an exception). If `False`, it returns immediately and yields `False` if the lock could not be acquired. Note that the context body is **always executed** regardless; check the yielded value to determine whether the lock was acquired.

- **`comment`** (default `None`) — Controls whether an SQL comment is appended to the lock statements with the `repr()` of the `lock_id` and the calling location. If `True`, the comment is always added. If `False`, it is never added. If `None` (the default), checks `settings.ADVISORY_LOCK_COMMENT`; if that is not set, falls back to `settings.DEBUG`.

- **`using`** (default `None`) — The database alias to use. If `None`, the default connection is used.

## Upgrading from 1.x

Version 2.0 includes several breaking changes:

- **String lock IDs hash differently.** The hashing algorithm changed from 32-bit CRC32 to 64-bit SHA-256. If your application relies on string-based lock IDs, existing locks will use different integer values. This only matters if you have external systems or other code that computes lock IDs independently; if you only use `advisory_lock` to acquire and release, the change is transparent.

- **Keyword-only arguments.** `shared`, `wait`, `comment`, and `using` must now be passed as keyword arguments:

  ```python
  # Before (1.x)
  advisory_lock("my_lock", True, False)

  # After (2.0)
  advisory_lock("my_lock", shared=True, wait=False)
  ```

- **Minimum versions** are now Python 3.10+ and Django 4.2+.

- The `six` dependency has been removed.

## Development

With local PostgreSQL:

```
uv sync
uv run pytest
```

With Docker Compose:

```
docker compose up -d
uv run pytest
docker compose down
```

To create the test database (if not using Docker):

```
createuser -s -P django_pglocks
createdb django_pglocks -O django_pglocks
```

## License

See `LICENSE.md`.
