from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from core.producer import send_statistics
from post.models import Post


@receiver(signal=post_save, sender=Post)
def post_create_update_handler(instance: Post, *args, **kwargs):
    send_statistics(instance)


@receiver(signal=m2m_changed, sender=Post.liked_by.through)
def post_m2m_change_liked_by_handler(instance: Post, *args, **kwargs):
    send_statistics(instance)
