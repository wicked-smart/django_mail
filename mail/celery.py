
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project3_cs50.settings")
app = Celery("mail")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()