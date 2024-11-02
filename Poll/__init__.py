from __future__ import absolute_import, unicode_literals

# Это обеспечит, что приложение Celery будет всегда импортировано при запуске Django
from .celery import app as celery_app

__all__ = ('celery_app',)
