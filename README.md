# django-pglocks

> **This package is deprecated.** Its functionality has moved to
> **[django-pgware](https://github.com/Xof/django-pgware)**.
>
> ```bash
> pip install django-pgware
> ```
>
> ```python
> # Old:
> from django_pglocks import advisory_lock
>
> # New (django-pgware installs as `django-pgware`, imports as `django_pg_utils`):
> from django_pg_utils import advisory_lock
> ```
>
> This package (2.1.0) is a final compatibility shim: it depends on `django-pgware`
> and re-exports `advisory_lock`/`async_advisory_lock` with a `DeprecationWarning`.
> It will not receive further updates.
