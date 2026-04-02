from __future__ import annotations

import pytest

from django_pglocks import async_advisory_lock


class TestAsyncAdvisoryLockBasic:
    @pytest.mark.django_db(transaction=True)
    async def test_tuple_lock_acquired_and_released(self) -> None:
        async with async_advisory_lock((5, 9)) as acquired:
            assert acquired is True

    @pytest.mark.django_db(transaction=True)
    async def test_int_lock_acquired_and_released(self) -> None:
        async with async_advisory_lock(123) as acquired:
            assert acquired is True

    @pytest.mark.django_db(transaction=True)
    async def test_string_lock_acquired(self) -> None:
        async with async_advisory_lock("test_lock") as acquired:
            assert acquired is True

    @pytest.mark.django_db(transaction=True)
    async def test_invalid_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Cannot use"):
            async with async_advisory_lock(3.14):  # type: ignore[arg-type]
                pass


class TestAsyncAdvisoryLockShared:
    @pytest.mark.django_db(transaction=True)
    async def test_shared_lock_acquired(self) -> None:
        async with async_advisory_lock(123, shared=True) as acquired:
            assert acquired is True


class TestAsyncAdvisoryLockNoWait:
    @pytest.mark.django_db(transaction=True)
    async def test_nowait_acquires_when_free(self) -> None:
        async with async_advisory_lock(456, wait=False) as acquired:
            assert acquired is True

    @pytest.mark.django_db(transaction=True)
    async def test_nowait_returns_false_when_held(self, second_connection) -> None:
        cur = second_connection.cursor()
        cur.execute("SELECT pg_advisory_lock(789)")
        cur.fetchone()
        try:
            async with async_advisory_lock(789, wait=False) as acquired:
                assert acquired is False
        finally:
            cur.execute("SELECT pg_advisory_unlock(789)")
            cur.fetchone()
            cur.close()


class TestAsyncAdvisoryLockComment:
    @pytest.mark.django_db(transaction=True)
    async def test_comment_true_adds_comment(self) -> None:
        async with async_advisory_lock((5, 9), comment=True) as acquired:
            assert acquired is True


class TestAsyncAdvisoryLockExceptionSafety:
    @pytest.mark.django_db(transaction=True)
    async def test_lock_released_on_exception(self) -> None:
        with pytest.raises(RuntimeError, match="boom"):
            async with async_advisory_lock((5, 9)) as acquired:
                assert acquired is True
                raise RuntimeError("boom")
        # Verify lock can be re-acquired after exception cleanup.
        async with async_advisory_lock((5, 9), wait=False) as re_acquired:
            assert re_acquired is True
