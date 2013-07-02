__version__ = '1.0'

from contextlib import contextmanager

from django.db import DEFAULT_DB_ALIAS, connections, transaction

@contextmanager
def advisory_lock(lock_id, shared=False, wait=True, using=None):
    if using is None:
        using = DEFAULT_DB_ALIAS

    # Django 1.5 uses .is_managed(); Django 1.6 has a public interface of .get_autocommit(); this allows
    # for either.

    try:
        in_transaction = not transaction.get_autocommit(using)
    except AttributeError:
        in_transaction = connections[using].is_managed()

    # Assemble the function name based on the options.

    function_name = 'pg_'

    if not wait:
        function_name += 'try_'

    function_name += 'advisory_'

    if in_transaction:
        function_name += 'xact_'

    function_name += 'lock'

    if shared:
        function_name += '_shared'

    if not in_transaction:
        release_function_name = 'pg_advisory_unlock'
        if shared:
            release_function_name += '_shared'
    else:
        release_function_name = None

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

    acquired = cursor.fetchone()[0]

    try:
        yield acquired
    finally:
        if acquired and release_function_name:
            release_params = ( release_function_name, ) + params

            command = base % release_params
            cursor.execute(command)