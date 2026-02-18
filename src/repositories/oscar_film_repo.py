from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.oscar_film import OscarFilm
from src.repositories.base_repository import BaseRepository


class OscarFilmRepo(BaseRepository[OscarFilm]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, OscarFilm)

    async def get_by_job_id(self, job_id: str) -> list[OscarFilm]:
        result = await self.session.execute(
            select(OscarFilm).where(OscarFilm.job_id == job_id)
        )
        return list(result.scalars().all())
