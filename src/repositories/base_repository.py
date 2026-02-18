from typing import Generic, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base_entity import BaseEntity

# T aceita qualquer model que herde de BaseEntity (dry)
T = TypeVar("T", bound=BaseEntity)


# repo generico: qualquer repo filho herda get, create, list sem reescrever
class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model_class: type[T]):
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, record_id) -> T | None:
        return await self.session.get(self.model_class, record_id)

    async def get_all(self) -> Sequence[T]:
        result = await self.session.execute(select(self.model_class))
        return result.scalars().all()

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        # flush envia pro banco mas nao commita, quem commita e a rota/handler
        await self.session.flush()
        return entity

    async def create_many(self, entities: list[T]) -> list[T]:
        self.session.add_all(entities)
        # flush envia pro banco mas nao commita, quem commita e a rota/handler
        await self.session.flush()
        return entities
