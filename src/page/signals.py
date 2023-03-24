from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from core.producer import send_statistics
from page.models import Page


@receiver(signal=post_save, sender=Page)
def page_create_update_handler(instance, *args, **kwargs):
    send_statistics(instance)


@receiver(signal=m2m_changed, sender=Page.followers.through)
def page_m2m_change_followers_handler(instance, *args, **kwargs):
    send_statistics(instance)


@receiver(signal=m2m_changed, sender=Page.follow_requests.through)
def page_m2m_change_follow_requests_handler(instance, *args, **kwargs):
    send_statistics(instance)
