import json
import logging

from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from services import LocalstackDynamoDB
from settings import (RABBIT_STATISTIC_QUEUE, RABBITMQ_HOST,
                      RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(event, context):
    credentials = PlainCredentials(
        username=RABBITMQ_DEFAULT_USER,
        password=RABBITMQ_DEFAULT_PASS
    )
    connection = BlockingConnection(
        ConnectionParameters(host=RABBITMQ_HOST,
                             credentials=credentials,
                             blocked_connection_timeout=300)
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBIT_STATISTIC_QUEUE)

    def callback(ch, method, properties, body):
        body_dict = json.loads(body.decode('utf-8'))
        LocalstackDynamoDB().put_item(body_dict)

    channel.basic_consume(queue=RABBIT_STATISTIC_QUEUE,
                          on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
