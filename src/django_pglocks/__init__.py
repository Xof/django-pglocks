import warnings

warnings.warn(
    "django-pglocks has been consolidated into django-pgware. "
    "Install django-pgware (it imports as django_pg_utils) and update "
    "imports to django_pg_utils.locks. "
    "This compatibility package will not receive further updates.",
    DeprecationWarning,
    stacklevel=2,
)

from django_pg_utils.locks import advisory_lock, async_advisory_lock

__all__ = ["advisory_lock", "async_advisory_lock"]
