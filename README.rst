==============
django-pglocks
==============

django-pglocks provides a useful context manager to manage PostgreSQL advisory locks. It requires Django (tested with 1.5), PostgreSQL, and (probably psycopg2.

Advisory locks are application-level locks that are acquired and released purely by the client of the database; PostgreSQL never acquires them on its own. They are very useful as a way of signalling to other sessions that a higher-level resource than a single row is in use, without having to lock an entire table or some other structure.

It's entirely up to the application to correctly acquire the right lock.

Advisory locks are either session locks or transaction locks. A session lock is held until the database session disconnects (or is reset); a transaction lock is held until the transaction terminates. If ``advisory_lock`` is called with a transaction (managed by Django) currently open, a transaction lock is created; otherwise, a session lock is.

Usage example::

    from django_pglocks import advisory_lock 
    
    lock_id = 'some lock'
    
    with advisory_lock(lock_id) as acquired:
        # code that should be inside of the lock.
        
The context manager attempts to take the lock, and then executes the code inside the context with the lock acquired. The lock is released when the context exits, either normally or via exception.

The parameters are:

* ``lock_id`` -- The ID of the lock to acquire. It can be a string, long, or a tuple of two ints. If it's a string, the hash of the string is used as the lock ID (PostgreSQL advisory lock IDs are 64 bit values).

* ``shared`` (default False) -- If true, a shared lock is taken. Any number of sessions can hold a shared lock; if another session attempts to take an exclusive lock, it will wait until all shared locks are released; if a session is holding a shared lock, it will block attempts to take a shared lock.

* ``wait`` (default True) -- If true, the context manager will wait until the lock has been acquired before executing the content; in that case, it always returns True (unless a deadlock occurs, in which case an exception is thrown). If false, the context manager will return immediately even if it cannot take the lock, in which case it returns false. Note that the context body is *always* executed; the only way to tell in the ``wait=False`` case whether or not the lock was acquired is to check the returned value.

* ``using`` (default None) -- The database alias on which to attempt to acquire the lock. If None, the default connection is used.