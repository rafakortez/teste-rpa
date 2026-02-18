import json

import aio_pika

from src.queue.rabbit_connection import QUEUE_NAME


async def publish_crawl_job(
    channel: aio_pika.abc.AbstractChannel,
    job_id: str,
    job_type: str,
) -> None:
    payload = {"job_id": job_id, "job_type": job_type}
    message = aio_pika.Message(
        body=json.dumps(payload).encode(),
        # salva em disco p nao perder reiniciando
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT, 
    )
    await channel.default_exchange.publish(
        message,
        routing_key=QUEUE_NAME,
    )
