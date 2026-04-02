from importlib.metadata import version

from django_pglocks._async import async_advisory_lock
from django_pglocks._sync import advisory_lock

__all__ = ["advisory_lock", "async_advisory_lock"]
__version__: str = version("django-pglocks")
