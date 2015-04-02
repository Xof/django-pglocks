__version__ = '1.0.3'

from contextdecorator import ContextDecorator
from zlib import crc32

class advisory_lock(ContextDecorator):

    def __init__(self, lock_id, shared=False, wait=True, using=None):
        self.lock_id = lock_id
        self.shared = shared
        self.wait = wait
        self.using = using

    def __enter__(self):
        from django.db import DEFAULT_DB_ALIAS, connections
        import six

        if self.using is None:
            self.using = DEFAULT_DB_ALIAS

        # Assemble the function name based on the options.

        function_name = 'pg_'

        if not self.wait:
            function_name += 'try_'

        function_name += 'advisory_lock'

        if self.shared:
            function_name += '_shared'

        self.release_function_name = 'pg_advisory_unlock'
        if self.shared:
            self.release_function_name += '_shared'

        # Format up the parameters.

        tuple_format = False

        if isinstance(self.lock_id, (list, tuple,)):
            if len(self.lock_id) != 2:
                raise ValueError("Tuples and lists as lock IDs must have exactly two entries.")

            if not isinstance(self.lock_id[0], six.integer_types) or not isinstance(self.lock_id[1], six.integer_types):
                raise ValueError("Both members of a tuple/list lock ID must be integers")

            tuple_format = True
        elif isinstance(self.lock_id, six.string_types):
            # Generates an id within postgres integer range (-2^31 to 2^31 - 1).
            # crc32 generates an unsigned integer in Py3, we convert it into
            # a signed integer using 2's complement (this is a noop in Py2)
            pos = crc32(self.lock_id.encode("utf-8"))
            self.lock_id = (2**31 - 1) & pos
            if pos & 2**31:
                self.lock_id -= 2**31
        elif not isinstance(self.lock_id, six.integer_types):
            raise ValueError("Cannot use %s as a lock id" % self.lock_id)

        if tuple_format:
            self.base = "SELECT %s(%d, %d)"
            self.params = (self.lock_id[0], self.lock_id[1],)
        else:
            self.base = "SELECT %s(%d)"
            self.params = (self.lock_id,)

        acquire_params = ( function_name, ) + self.params

        command = self.base % acquire_params
        self.cursor = connections[self.using].cursor()

        self.cursor.execute(command)

        if not self.wait:
            self.acquired = self.cursor.fetchone()[0]
        else:
            self.acquired = True

        return self.acquired

    def __exit__(self, *exc):
        if self.acquired:
            release_params = ( self.release_function_name, ) + self.params

            command = self.base % release_params
            self.cursor.execute(command)

        self.cursor.close()
