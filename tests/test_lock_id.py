from __future__ import annotations

from typing import Any

import pytest

from django_pglocks._lock import (
    build_comment,
    build_lock_sql,
    resolve_comment_setting,
    resolve_lock_id,
)


class TestResolveLockIdString:
    def test_string_returns_int(self) -> None:
        result = resolve_lock_id("test")
        assert isinstance(result, int)

    def test_string_is_deterministic(self) -> None:
        assert resolve_lock_id("hello") == resolve_lock_id("hello")

    def test_different_strings_differ(self) -> None:
        assert resolve_lock_id("foo") != resolve_lock_id("bar")

    def test_string_within_64_bit_range(self) -> None:
        result = resolve_lock_id("test")
        assert -(2**63) <= result <= 2**63 - 1

    def test_empty_string(self) -> None:
        result = resolve_lock_id("")
        assert isinstance(result, int)

    def test_long_string(self) -> None:
        result = resolve_lock_id("x" * 10000)
        assert isinstance(result, int)


class TestResolveLockIdInt:
    def test_int_passthrough(self) -> None:
        assert resolve_lock_id(42) == 42

    def test_negative_int(self) -> None:
        assert resolve_lock_id(-1) == -1

    def test_zero(self) -> None:
        assert resolve_lock_id(0) == 0

    def test_max_bigint(self) -> None:
        val = 2**63 - 1
        assert resolve_lock_id(val) == val

    def test_min_bigint(self) -> None:
        val = -(2**63)
        assert resolve_lock_id(val) == val


class TestResolveLockIdTuple:
    def test_tuple_passthrough(self) -> None:
        assert resolve_lock_id((5, 9)) == (5, 9)

    def test_list_normalized_to_tuple(self) -> None:
        assert resolve_lock_id([5, 9]) == (5, 9)

    def test_wrong_length_tuple(self) -> None:
        with pytest.raises(ValueError, match="exactly two"):
            resolve_lock_id((1,))

    def test_wrong_length_triple(self) -> None:
        with pytest.raises(ValueError, match="exactly two"):
            resolve_lock_id((1, 2, 3))

    def test_non_int_tuple_member(self) -> None:
        with pytest.raises(ValueError, match="integers"):
            resolve_lock_id((1, "a"))

    def test_empty_tuple(self) -> None:
        with pytest.raises(ValueError, match="exactly two"):
            resolve_lock_id(())


class TestResolveLockIdInvalid:
    def test_float_rejected(self) -> None:
        with pytest.raises(ValueError, match="Cannot use"):
            resolve_lock_id(3.14)  # type: ignore[arg-type]

    def test_none_rejected(self) -> None:
        with pytest.raises(ValueError, match="Cannot use"):
            resolve_lock_id(None)  # type: ignore[arg-type]

    def test_object_rejected(self) -> None:
        with pytest.raises(ValueError, match="Cannot use"):
            resolve_lock_id(object())  # type: ignore[arg-type]


class TestBuildLockSql:
    def test_single_int_no_comment(self) -> None:
        sql, params = build_lock_sql("pg_advisory_lock", 42, "")
        assert sql == "SELECT pg_advisory_lock(%s) "
        assert params == (42,)

    def test_single_int_with_comment(self) -> None:
        sql, params = build_lock_sql("pg_advisory_lock", 42, "-- test comment")
        assert sql == "SELECT pg_advisory_lock(%s) -- test comment"
        assert params == (42,)

    def test_tuple_no_comment(self) -> None:
        sql, params = build_lock_sql("pg_advisory_lock", (5, 9), "")
        assert sql == "SELECT pg_advisory_lock(%s, %s) "
        assert params == (5, 9)

    def test_tuple_with_comment(self) -> None:
        sql, params = build_lock_sql("pg_try_advisory_lock_shared", (5, 9), "-- locked")
        assert sql == "SELECT pg_try_advisory_lock_shared(%s, %s) -- locked"
        assert params == (5, 9)


class TestBuildComment:
    def test_returns_string(self) -> None:
        result = build_comment("my_lock")
        assert isinstance(result, str)

    def test_contains_lock_id_repr(self) -> None:
        result = build_comment("my_lock")
        assert "'my_lock'" in result

    def test_contains_filename(self) -> None:
        result = build_comment("my_lock")
        assert "test_lock_id.py" in result

    def test_starts_with_sql_comment(self) -> None:
        result = build_comment("my_lock")
        assert result.startswith("-- ")

    def test_contains_line_number(self) -> None:
        result = build_comment(42)
        assert " @ " in result

    def test_tuple_lock_id(self) -> None:
        result = build_comment((5, 9))
        assert "(5, 9)" in result


class TestResolveCommentSetting:
    def test_true_returns_true(self) -> None:
        assert resolve_comment_setting(True) is True

    def test_false_returns_false(self) -> None:
        assert resolve_comment_setting(False) is False

    def test_none_checks_advisory_lock_comment(self, settings: Any) -> None:
        settings.ADVISORY_LOCK_COMMENT = True
        assert resolve_comment_setting(None) is True

    def test_none_falls_back_to_debug(self, settings: Any) -> None:
        if hasattr(settings, "ADVISORY_LOCK_COMMENT"):
            del settings.ADVISORY_LOCK_COMMENT
        settings.DEBUG = True
        assert resolve_comment_setting(None) is True

    def test_none_defaults_false(self, settings: Any) -> None:
        if hasattr(settings, "ADVISORY_LOCK_COMMENT"):
            del settings.ADVISORY_LOCK_COMMENT
        settings.DEBUG = False
        assert resolve_comment_setting(None) is False
