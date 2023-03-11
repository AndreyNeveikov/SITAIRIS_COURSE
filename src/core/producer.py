import json

from django.conf import settings
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

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
