from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField(to=Tag, related_name='pages', blank=True)
    owner = models.ForeignKey(to='user.User',
                              on_delete=models.CASCADE,
                              related_name='pages')
    followers = models.ManyToManyField(to='user.User',
                                       related_name='follows')
    image = models.URLField(null=True, blank=True)
    is_private = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField(to='user.User',
                                             related_name='requests')
    is_blocked = models.BooleanField(default=False)
    unblock_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.unblock_date is not None:
            if self.unblock_date < timezone.now():
                raise ValidationError(
                    {'error': 'The date cannot be in the past.'}
                )
        super().save(*args, **kwargs)
