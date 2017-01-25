from django.db import connection
from django.test import TransactionTestCase

from django_pglocks import advisory_lock, advisory_lock_acquired


class PgLocksTests(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        cursor = connection.cursor()
        cursor.execute(
                "SELECT oid FROM pg_database WHERE datname = %s",
                [connection.settings_dict['NAME']])
        cls.db_oid = cursor.fetchall()[0][0]
        cursor.close()

    def assertNumLocks(self, expected):
        cursor = connection.cursor()
        cursor.execute(
                "SELECT COUNT(*) FROM pg_locks WHERE database = %s AND locktype = %s",
                [self.db_oid, 'advisory'])
        actual = cursor.fetchall()[0][0]
        cursor.close()
        self.assertEqual(actual, expected)

    def test_basic_lock_str(self):
        self.assertNumLocks(0)
        with advisory_lock('test') as acquired:
            self.assertTrue(acquired)
            self.assertNumLocks(1)
        self.assertNumLocks(0)

    def test_basic_lock_int(self):
        self.assertNumLocks(0)
        with advisory_lock(123) as acquired:
            self.assertTrue(acquired)
            self.assertNumLocks(1)
        self.assertNumLocks(0)

    def test_basic_lock_tuple(self):
        self.assertNumLocks(0)
        with advisory_lock(123, 456) as acquired:
            self.assertTrue(acquired)
            self.assertNumLocks(1)
        self.assertNumLocks(0)

    def test_lock_acquired(self):
        self.assertFalse(advisory_lock_acquired(234))
        with advisory_lock(234) as acquired:
            self.assertTrue(acquired)
            self.assertTrue(advisory_lock_acquired(234))
        self.assertFalse(advisory_lock_acquired(234))
