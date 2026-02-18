from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings

engine = create_async_engine(settings.database_url, echo=False)

async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    # sem isso, acessar atributos apos commit levanta erro em async
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
