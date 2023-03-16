import json

from django.conf import settings
from django.db.models import Sum
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

from post.models import Post

credentials = PlainCredentials(
    username=settings.RABBITMQ_DEFAULT_USER,
    password=settings.RABBITMQ_DEFAULT_PASS
)
connection = BlockingConnection(
    ConnectionParameters(host=settings.RABBITMQ_HOST,
                         credentials=credentials,
                         heartbeat=600,
                         blocked_connection_timeout=300)
)
channel = connection.channel()
channel.queue_declare(queue=settings.RABBIT_STATISTIC_QUEUE)


def publish(body):
    channel.basic_publish(exchange='',
                          routing_key=settings.RABBIT_STATISTIC_QUEUE,
                          body=json.dumps(body).encode())


def send_statistics(instance):
    if isinstance(instance, Post):
        instance = instance.page
    user_uuid = instance.owner.uuid
    page_id = instance.id
    likes = instance.posts.aggregate(Sum('liked_by')).get('liked_by__sum')
    likes_count = int(likes) if likes else 0
    posts = instance.posts.count()
    followers = instance.followers.count()
    follow_requests = instance.follow_requests.count()
    statistics = {'user_uuid': str(user_uuid),
                  'page_id': str(page_id),
                  'likes': str(likes_count),
                  'posts': str(posts),
                  'followers': str(followers),
                  'follow_requests': str(follow_requests)}
    publish(statistics)
