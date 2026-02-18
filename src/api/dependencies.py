import asyncio
import logging

import aio_pika
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_factory
from src.queue.rabbit_connection import get_rabbit_channel, get_rabbit_connection

logger = logging.getLogger(__name__)


async def get_session() -> AsyncSession:
    """Abre sessao do banco, fecha automaticamente ao sair da rota."""
    async with async_session_factory() as session:
        yield session


# conexao unica reutilizada entre requests (criada no startup da app)
_rabbit_connection: aio_pika.abc.AbstractRobustConnection | None = None


async def startup_rabbit():
    """Conecta no RabbitMQ com retry p/ lidar com startup lento do container."""
    global _rabbit_connection
    for attempt in range(10):
        try:
            _rabbit_connection = await get_rabbit_connection()
            logger.info("RabbitMQ conectado na tentativa %d", attempt + 1)
            return
        except Exception:
            logger.warning("RabbitMQ indisponivel, tentativa %d/10...", attempt + 1)
            await asyncio.sleep(3)


async def shutdown_rabbit():
    """Chamada quando a API para."""
    global _rabbit_connection
    if _rabbit_connection:
        await _rabbit_connection.close()


async def get_channel() -> aio_pika.abc.AbstractChannel:
    """Abre canal do RabbitMQ por request, fecha ao sair da rota."""
    channel = await get_rabbit_channel(_rabbit_connection)
    try:
        yield channel
    finally:
        await channel.close()
