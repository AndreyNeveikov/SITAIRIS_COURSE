from rest_framework.generics import get_object_or_404

from core.services import LocalstackManager
from innotter.celery import app
from page.models import Page


@app.task()
def unblock_page_at_specified_date(page_id):
    page = get_object_or_404(Page, id=page_id)
    page.is_blocked = False
    page.unblock_date = None
    page.save()


@app.task()
def send_email(data):
    LocalstackManager.send_email(data)
