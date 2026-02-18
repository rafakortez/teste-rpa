import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings
from src.models.base_entity import BaseEntity

# imports parecem não usados mas registram models no metadata do Alembic
# sem eles, Alembic nao sabe quais tabelas criar
from src.models.crawl_job import CrawlJob  # noqa: F401
from src.models.hockey_team import HockeyTeam  # noqa: F401
from src.models.oscar_film import OscarFilm  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# metadata contem a definicao de todas tabelas dos models importados acima
target_metadata = BaseEntity.metadata


def run_migrations_offline():
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
