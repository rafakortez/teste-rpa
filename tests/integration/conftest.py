import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from src.models.base_entity import BaseEntity


@pytest.fixture(scope="session")
def postgres_url():
    """Sobe container Postgres real via Testcontainers, retorna URL de conexao."""
    with PostgresContainer("postgres:16-alpine") as pg:
        # testcontainers gera porta aleatoria pra evitar conflitos
        url = pg.get_connection_url().replace("psycopg2", "asyncpg")
        yield url


@pytest.fixture
async def session(postgres_url):
    """Cria tabelas e sessao por teste, limpa tudo ao final."""
    engine = create_async_engine(postgres_url)

    async with engine.begin() as conn:
        await conn.run_sync(BaseEntity.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(BaseEntity.metadata.drop_all)

    await engine.dispose()
