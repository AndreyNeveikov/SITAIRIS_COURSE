# Generated by Django 4.1.7 on 2023-05-09 12:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("post", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("page", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="liked_by",
            field=models.ManyToManyField(
                blank=True,
                default=None,
                related_name="likes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="page",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posts",
                to="page.page",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="reply_to",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="replies",
                to="post.post",
            ),
        ),
    ]
