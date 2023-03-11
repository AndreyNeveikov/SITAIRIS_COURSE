from django.db.models.signals import post_save
from django.dispatch import receiver

from core.producer import publish
from page.models import Page


@receiver(signal=post_save, sender=Page)
def page_create_update_handler(instance, *args, **kwargs):
    publish(instance.id)
