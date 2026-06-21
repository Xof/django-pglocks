import warnings

# Re-export from the successor package. Imports stay at module top (ruff E402);
# the deprecation warning below still fires on first import either way.
from django_pg_utils.locks import advisory_lock, async_advisory_lock

warnings.warn(
    "django-pglocks has been consolidated into django-pgware. "
    "Install django-pgware (it imports as django_pg_utils) and update "
    "imports to django_pg_utils.locks. "
    "This compatibility package will not receive further updates.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["advisory_lock", "async_advisory_lock"]
