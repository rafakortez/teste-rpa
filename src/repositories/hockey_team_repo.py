from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.hockey_team import HockeyTeam
from src.repositories.base_repository import BaseRepository


class HockeyTeamRepo(BaseRepository[HockeyTeam]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, HockeyTeam)

    async def get_by_job_id(self, job_id: str) -> list[HockeyTeam]:
        result = await self.session.execute(
            select(HockeyTeam).where(HockeyTeam.job_id == job_id)
        )
        return list(result.scalars().all())
