import asyncio
import json

from aio_pika import connect_robust, abc

from services import LocalstackLambda, logger
from settings import RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS, \
    RABBITMQ_HOST, RABBIT_STATISTIC_QUEUE, RABBITMQ_PORT


async def consume():
    connection = await connect_robust(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        loop=asyncio.get_running_loop(),
        login=RABBITMQ_DEFAULT_USER,
        password=RABBITMQ_DEFAULT_PASS
    )

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue(RABBIT_STATISTIC_QUEUE)
    await queue.consume(callback)


async def callback(message: abc.AbstractIncomingMessage):
    async with message.process():
        try:
            message = json.loads(message.body.decode())
            logger.info(f"Message received: {message}")
            LocalstackLambda().invoke_function(function_name='handler',
                                               payload=json.dumps(
                                                   message).encode('utf-8'))
        except Exception as e:
            logger.error(e)
