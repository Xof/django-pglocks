__version__ = '1.0.2'

from contextlib import contextmanager

@contextmanager
def advisory_lock(lock_id, shared=False, wait=True, using=None):

    from django.db import DEFAULT_DB_ALIAS, connections, transaction

    if using is None:
        using = DEFAULT_DB_ALIAS

    # Assemble the function name based on the options.

    function_name = 'pg_'

    if not wait:
        function_name += 'try_'

    function_name += 'advisory_lock'

    if shared:
        function_name += '_shared'

    release_function_name = 'pg_advisory_unlock'
    if shared:
        release_function_name += '_shared'

    # Format up the parameters.

    tuple_format = False

    if isinstance(lock_id, (list, tuple,)):
        if len(lock_id) != 2:
            raise ValueError("Tuples and lists as lock IDs must have exactly two entries.")

        if not isinstance(lock_id[0], (int, long,)) or not isinstance(lock_id[1], (int, long,)):
            raise ValueError("Both members of a tuple/list lock ID must be ints or longs")

        tuple_format = True
    elif not isinstance(lock_id, (int, long,)):
        lock_id = long(lock_id.__hash__())

    if tuple_format:
        base = "SELECT %s(%d, %d)"
        params = (lock_id[0], lock_id[1],)
    else:
        base = "SELECT %s(%d)"
        params = (lock_id,)

    acquire_params = ( function_name, ) + params

    command = base % acquire_params
    cursor = connections[using].cursor()

    cursor.execute(command)

    if not wait:
        acquired = cursor.fetchone()[0]
    else:
        acquired = True

    try:
        yield acquired
    finally:
        if acquired:
            release_params = ( release_function_name, ) + params

            command = base % release_params
            cursor.execute(command)

        cursor.close()
