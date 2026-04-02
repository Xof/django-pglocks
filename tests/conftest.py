from __future__ import annotations

import pytest
from django.db import connections


@pytest.fixture
def db_cursor(db: None) -> None:
    """Marker fixture that ensures the test database is available."""


@pytest.fixture
def second_connection(db: None):
    """Provide a second database connection for contention tests.

    Uses a raw psycopg connection so it has its own session, independent
    of Django's connection pooling.
    """
    # Filter out Django-specific params that psycopg2.connect() doesn't accept.
    _DJANGO_ONLY_PARAMS = {"cursor_factory"}
    raw_params = {
        k: v
        for k, v in connections["default"].get_connection_params().items()
        if k not in _DJANGO_ONLY_PARAMS
    }
    raw_conn = connections["default"].Database.connect(**raw_params)
    raw_conn.autocommit = True
    yield raw_conn
    raw_conn.close()
