from django.db import models

from page.models import Tag


class Post(models.Model):
    page = models.ForeignKey(to='page.Page',
                             on_delete=models.CASCADE,
                             related_name='posts')
    title = models.CharField(max_length=60)
    content = models.CharField(max_length=200)
    tags = models.ManyToManyField(to=Tag, related_name='post', blank=True)
    reply_to = models.ForeignKey(to='Post',
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    liked_by = models.ManyToManyField(to='user.User',
                                      default=None,
                                      blank=True,
                                      related_name='likes')
