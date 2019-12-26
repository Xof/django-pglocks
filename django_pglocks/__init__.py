__version__ = '1.0.4'

from contextlib import contextmanager
from zlib import crc32

@contextmanager
def advisory_lock(lock_id, shared=False, wait=True, using=None):

    import six
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

        if not isinstance(lock_id[0], six.integer_types) or not isinstance(lock_id[1], six.integer_types):
            raise ValueError("Both members of a tuple/list lock ID must be integers")

        tuple_format = True
    elif isinstance(lock_id, six.string_types):
        # Generates an id within postgres integer range (-2^31 to 2^31 - 1).
        # crc32 generates an unsigned integer in Py3, we convert it into
        # a signed integer using 2's complement (this is a noop in Py2)
        pos = crc32(lock_id.encode("utf-8"))
        lock_id = (2**31 - 1) & pos
        if pos & 2**31:
            lock_id -= 2**31
    elif not isinstance(lock_id, six.integer_types):
        raise ValueError("Cannot use %s as a lock id" % lock_id)

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
