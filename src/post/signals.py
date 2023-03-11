from django.db.models import Sum
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from core.producer import publish
from post.models import Post


@receiver(signal=m2m_changed, sender=Post)
def post_create_update_handler(instance: Post, *args, **kwargs):
    print(args, kwargs)
    publish({'page_id': str(instance.page.id),
             'likes': int(instance.page.posts.aggregate(Sum('liked_by')).get('liked_by__sum', 0)),
             'posts': instance.page.posts.count(),
             'followers': instance.page.followers.count()})
