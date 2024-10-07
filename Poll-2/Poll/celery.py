from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установите переменную окружения DJANGO_SETTINGS_MODULE для приложения celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Poll.settings')

app = Celery('Poll')

# Используйте строку конфигурации для Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически загружать задачи из всех установленных приложений Django
app.autodiscover_tasks()
