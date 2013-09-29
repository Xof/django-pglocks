import threading
import time

from django.db import connection
from django.test import TransactionTestCase

from django_pglocks import advisory_lock


TIME_UNIT = 0.01


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

    def test_lock(self):
        self.assertNumLocks(0)
        with advisory_lock('test') as acquired:
            self.assertIsNone(acquired)
            self.assertNumLocks(1)
        self.assertNumLocks(0)

    def test_wait(self):
        lock_acquired = threading.Event()

        def run1():
            # This thread will acquire the lock and force the other to wait.
            try:
                with advisory_lock('test') as acquired:
                    self.assertIsNone(acquired)
                    lock_acquired.set()
                    time.sleep(2 * TIME_UNIT)
            finally:
                connection.close()

        def run2():
            # This thread will wait until the other releases the lock.
            try:
                lock_acquired.wait(TIME_UNIT)
                t0 = time.time()
                with advisory_lock('test') as acquired:
                    self.assertIsNone(acquired)
                t1 = time.time()
                self.assertTrue(TIME_UNIT < t1 - t0 < 3 * TIME_UNIT)
            finally:
                connection.close()

        t1 = threading.Thread(target=run1)
        t2 = threading.Thread(target=run2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def test_nowait(self):
        lock_acquired = threading.Event()

        def run1():
            # This thread will acquire the lock and force the other to wait.
            try:
                with advisory_lock('test', wait=False) as acquired:
                    self.assertTrue(acquired)
                    lock_acquired.set()
                    time.sleep(2 * TIME_UNIT)
            finally:
                connection.close()

        def run2():
            # This thread will wait until the other releases the lock.
            try:
                lock_acquired.wait(TIME_UNIT)
                t0 = time.time()
                with advisory_lock('test', wait=False) as acquired:
                    self.assertFalse(acquired)
                t1 = time.time()
                self.assertTrue(t1 - t0 < TIME_UNIT)
            finally:
                connection.close()

        t1 = threading.Thread(target=run1)
        t2 = threading.Thread(target=run2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def test_shared(self):
        lock_acquired = threading.Event()

        def run1():
            # This thread will acquire the lock and force the other to wait.
            try:
                with advisory_lock('test', shared=True) as acquired:
                    self.assertIsNone(acquired)
                    lock_acquired.set()
                    time.sleep(2 * TIME_UNIT)
            finally:
                connection.close()

        def run2():
            # This thread will wait until the other releases the lock.
            try:
                lock_acquired.wait(TIME_UNIT)
                t0 = time.time()
                with advisory_lock('test', shared=True) as acquired:
                    self.assertIsNone(acquired)
                t1 = time.time()
                self.assertTrue(t1 - t0 < TIME_UNIT)
            finally:
                connection.close()

        t1 = threading.Thread(target=run1)
        t2 = threading.Thread(target=run2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def test_ids(self):
        # Arbitrary ids
        with advisory_lock(object):
            self.assertNumLocks(1)

        # Incorrect arbitrary ids
        with self.assertRaises(TypeError):
            with advisory_lock({}):
                pass

        # Explicit ids
        with advisory_lock(1):
            self.assertNumLocks(1)
        with advisory_lock([1, 2]):
            self.assertNumLocks(1)

        # Incorrect explicit ids
        with self.assertRaises(ValueError):
            with advisory_lock([1]):
                pass
        with self.assertRaises(ValueError):
            with advisory_lock(['a', 'b']):
                pass
        with self.assertRaises(ValueError):
            with advisory_lock([1, 2, 3]):
                pass
