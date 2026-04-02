from __future__ import annotations

import pytest
from django.db import DEFAULT_DB_ALIAS, connections

from django_pglocks import advisory_lock


def _check_advisory_lock_held(classid: int, objid: int) -> bool:
    """Check if an advisory lock is held by the current backend."""
    with connections[DEFAULT_DB_ALIAS].cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM pg_locks
            WHERE locktype = 'advisory'
              AND classid = %s
              AND objid = %s
              AND pid = pg_backend_pid()
            """,
            [classid, objid],
        )
        return cursor.fetchone() is not None


def _check_single_id_lock_held(lock_id: int) -> bool:
    """Check if a single-ID advisory lock is held by the current backend."""
    with connections[DEFAULT_DB_ALIAS].cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM pg_locks
            WHERE locktype = 'advisory'
              AND objid = %s
              AND pid = pg_backend_pid()
            """,
            [lock_id],
        )
        return cursor.fetchone() is not None


class TestSyncAdvisoryLockBasic:
    @pytest.mark.django_db
    def test_tuple_lock_acquired_and_released(self) -> None:
        with advisory_lock((5, 9)) as acquired:
            assert acquired is True
            assert _check_advisory_lock_held(5, 9)
        assert not _check_advisory_lock_held(5, 9)

    @pytest.mark.django_db
    def test_int_lock_acquired_and_released(self) -> None:
        with advisory_lock(123) as acquired:
            assert acquired is True
            assert _check_single_id_lock_held(123)
        assert not _check_single_id_lock_held(123)

    @pytest.mark.django_db
    def test_string_lock_acquired(self) -> None:
        with advisory_lock("test_lock") as acquired:
            assert acquired is True

    @pytest.mark.django_db
    def test_invalid_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Cannot use"), advisory_lock(3.14):  # type: ignore[arg-type]
            pass


class TestSyncAdvisoryLockShared:
    @pytest.mark.django_db
    def test_shared_lock_acquired(self) -> None:
        with advisory_lock(123, shared=True) as acquired:
            assert acquired is True

    @pytest.mark.django_db
    def test_two_shared_locks(self, second_connection) -> None:
        """Two sessions can hold the same shared lock simultaneously."""
        with advisory_lock(999, shared=True) as acquired:
            assert acquired is True
            cur = second_connection.cursor()
            cur.execute("SELECT pg_try_advisory_lock_shared(999)")
            second_acquired = cur.fetchone()[0]
            assert second_acquired is True
            cur.execute("SELECT pg_advisory_unlock_shared(999)")
            cur.close()


class TestSyncAdvisoryLockNoWait:
    @pytest.mark.django_db
    def test_nowait_acquires_when_free(self) -> None:
        with advisory_lock(456, wait=False) as acquired:
            assert acquired is True

    @pytest.mark.django_db
    def test_nowait_returns_false_when_held(self, second_connection) -> None:
        """wait=False returns False when another session holds the lock."""
        cur = second_connection.cursor()
        cur.execute("SELECT pg_advisory_lock(789)")
        cur.fetchone()
        try:
            with advisory_lock(789, wait=False) as acquired:
                assert acquired is False
        finally:
            cur.execute("SELECT pg_advisory_unlock(789)")
            cur.fetchone()
            cur.close()


class TestSyncAdvisoryLockComment:
    @pytest.mark.django_db
    def test_comment_true_adds_comment(self) -> None:
        with advisory_lock((5, 9), comment=True) as acquired:
            assert acquired is True
        assert not _check_advisory_lock_held(5, 9)

    @pytest.mark.django_db
    def test_comment_false_overrides_debug(self, settings) -> None:
        settings.DEBUG = True
        with advisory_lock(123, comment=False) as acquired:
            assert acquired is True


class TestSyncAdvisoryLockExceptionSafety:
    @pytest.mark.django_db
    def test_lock_released_on_exception(self) -> None:
        with (
            pytest.raises(RuntimeError, match="boom"),
            advisory_lock((5, 9)) as acquired,
        ):
            assert acquired is True
            assert _check_advisory_lock_held(5, 9)
            raise RuntimeError("boom")
        assert not _check_advisory_lock_held(5, 9)
