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
