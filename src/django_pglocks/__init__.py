import warnings

warnings.warn(
    "django-pglocks has been consolidated into django-pg-utils. "
    "Install django-pg-utils and update imports to django_pg_utils.locks. "
    "This compatibility package will not receive further updates.",
    DeprecationWarning,
    stacklevel=2,
)

from django_pg_utils.locks import advisory_lock, async_advisory_lock

__all__ = ["advisory_lock", "async_advisory_lock"]
