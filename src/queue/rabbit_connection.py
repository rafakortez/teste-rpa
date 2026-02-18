import aio_pika

from src.config import settings

QUEUE_NAME = "crawl_jobs"


async def get_rabbit_connection() -> aio_pika.abc.AbstractRobustConnection:
    # robust reconecta sozinho se a conexao cair
    return await aio_pika.connect_robust(settings.rabbitmq_url)


async def get_rabbit_channel(
    connection: aio_pika.abc.AbstractRobustConnection,
) -> aio_pika.abc.AbstractChannel:
    channel = await connection.channel()
    # durable=True sobrevive restart do RabbitMQ (salva em disco)
    await channel.declare_queue(QUEUE_NAME, durable=True)
    return channel
