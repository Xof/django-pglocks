==============
django-pglocks
==============

django-pglocks provides a useful context manager to manage PostgreSQL advisory locks. It requires Django (tested with 1.5), PostgreSQL, and (probably) psycopg2.

Advisory Locks
==============

Advisory locks are application-level locks that are acquired and released purely by the client of the database; PostgreSQL never acquires them on its own. They are very useful as a way of signalling to other sessions that a higher-level resource than a single row is in use, without having to lock an entire table or some other structure.

It's entirely up to the application to correctly acquire the right lock.

Advisory locks are either session locks or transaction locks. A session lock is held until the database session disconnects (or is reset); a transaction lock is held until the transaction terminates.

Currently, the context manager only creates session locks, as the behavior of a lock persisting after the context body has been exited is surprising, and there's no way of releasing a transaction-scope advisory lock except to exit the transaction.

Installing
==========

Just use pip::

    pip install django-pglocks

Usage
=====

Usage example::

    from django_pglocks import advisory_lock

    lock_id = 'some lock'

    with advisory_lock(lock_id) as acquired:
        # code that should be inside of the lock.

The context manager attempts to take the lock, and then executes the code inside the context with the lock acquired. The lock is released when the context exits, either normally or via exception.

The parameters are:

* ``lock_id`` -- The ID of the lock to acquire. It can be a string, long, or a tuple of two ints. If it's a string, the hash of the string is used as the lock ID (PostgreSQL advisory lock IDs are 64 bit values).

* ``shared`` (default False) -- If True, a shared lock is taken. Any number of sessions can hold a shared lock; if another session attempts to take an exclusive lock, it will wait until all shared locks are released; if a session is holding a shared lock, it will block attempts to take a shared lock. If False (the default), an exclusive lock is taken.

* ``wait`` (default True) -- If True (the default), the context manager will wait until the lock has been acquired before executing the content; in that case, it always returns True (unless a deadlock occurs, in which case an exception is thrown). If False, the context manager will return immediately even if it cannot take the lock, in which case it returns false. Note that the context body is *always* executed; the only way to tell in the ``wait=False`` case whether or not the lock was acquired is to check the returned value.

* ``using`` (default None) -- The database alias on which to attempt to acquire the lock. If None, the default connection is used.

Contributing
============

To run the test suite, you must create a user and a database::

    $ createuser -s -P django_pglocks
    Enter password for new role: django_pglocks
    Enter it again: django_pglocks
    $ createdb django_pglocks -O django_pglocks

You can then run the tests with::

    $ DJANGO_SETTINGS_MODULE=django_pglocks.test_settings PYTHONPATH=. django-admin.py test

License
=======

It's released under the `MIT License <http://opensource.org/licenses/mit-license.php>`_.

Change History 1.0.3
====================

Enable use as a decorator.

Change History 1.0.2
====================

Fixed bug where lock would not be released when acquired with wait=False.
Many thanks to Aymeric Augustin for finding this!

Change History 1.0.1
====================

Removed transaction-level locks, as their behavior was somewhat surprising (having the lock persist after the context manager exited was unexpected behavior).
