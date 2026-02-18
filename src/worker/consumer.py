import asyncio
import json
import logging

import aio_pika

from src.database import async_session_factory
from src.queue.rabbit_connection import QUEUE_NAME, get_rabbit_channel, get_rabbit_connection
from src.worker.job_handler import handle_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def on_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    """Chamada automatica pra cada mmsg que chega na fila."""
    async with message.process():
        # process() envia ack automatico se nao der erro, re-queue se der
        payload = json.loads(message.body.decode())
        job_id = payload["job_id"]
        job_type = payload["job_type"]
        logger.info("Recebeu job %s tipo %s", job_id, job_type)

        async with async_session_factory() as session:
            await handle_job(session, job_id, job_type)


async def main() -> None:
    """Loop principal do worker. Roda ate ser interrompido."""
    connection = await get_rabbit_connection()
    channel = await get_rabbit_channel(connection)

    queue = await channel.get_queue(QUEUE_NAME)

    # prefetch=1: worker pega 1 msg por vez, so pega a proxima apos terminar
    await channel.set_qos(prefetch_count=1)

    logger.info("Worker escutando fila '%s'...", QUEUE_NAME)
    await queue.consume(on_message)

    # mantem o processo vivo esperando mensagens
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
