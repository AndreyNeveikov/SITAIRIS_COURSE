#
# import asyncio
# import json
# import logging
# import sched, time
#
# import aio_pika
#
#
# async def process_message(
#     message: aio_pika.abc.AbstractIncomingMessage,
# ) -> None:
#     async with message.process():
#         logging.info(message.body.decode())
#         await asyncio.sleep(1)
#
#
# async def main() -> None:
#     logging.basicConfig(level=logging.DEBUG)
#     connection = await aio_pika.connect_robust(
#         host="rabbitmq3",
#         login="admin",
#         password="admin",
#         loop=asyncio.get_running_loop()
#     )
#
#     queue_name = "statistics"
#
#     # Creating channel
#     channel = await connection.channel()
#
#     # Maximum message count which will be processing at the same time.
#     await channel.set_qos(prefetch_count=100)
#
#     # Declaring queue
#     queue = await channel.declare_queue(queue_name, auto_delete=False)
#
#     await queue.consume(process_message)
#
#     try:
#         # Wait until terminate
#         await asyncio.Future()
#     finally:
#         await connection.close()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())


from aio_pika import connect_robust, abc
import logging
import asyncio
import json

from settings import RABBIT_STATISTIC_QUEUE
from services import StatisticsRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def consume():
    connection = await connect_robust(
        host="rabbitmq3",
        login="admin",
        password="admin",
        loop=asyncio.get_running_loop()
    )

    channel = await connection.channel()
    queue = await channel.declare_queue(RABBIT_STATISTIC_QUEUE)
    await queue.consume(callback)


async def callback(message: abc.AbstractIncomingMessage):
    async with message.process():
        try:
            message = json.loads(message.body.decode())
            logger.info(f"Message received: {message}")
            # message_type = message['type']

            StatisticsRepository().put_item(message)

        except Exception as e:
            logger.error(e)
