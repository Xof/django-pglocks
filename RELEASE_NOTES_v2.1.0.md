## django-pglocks 2.1.0 — Final release

**This package is deprecated.** Its functionality now lives in
**[django-pgware](https://pypi.org/project/django-pgware/)**.

2.1.0 is a final compatibility shim: it depends on `django-pgware` and
re-exports `advisory_lock` / `async_advisory_lock` with a `DeprecationWarning`.
No further updates will be made here.

### Migrate

```bash
pip install django-pgware
```

```python
# Old:
from django_pglocks import advisory_lock
# New (django-pgware installs as `django-pgware`, imports as `django_pg_utils`):
from django_pg_utils import advisory_lock
```

### Notes

- Marked `Development Status :: 7 - Inactive` on PyPI.
- The PyPI summary now leads with `DEPRECATED`.
- Last functional release was 1.0.4; 2.x is shim-only.
