from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.crawl_job import CrawlJob, JobStatus
from src.repositories.base_repository import BaseRepository


class CrawlJobRepo(BaseRepository[CrawlJob]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CrawlJob)

    async def update_status(
        self, job_id: str, status: JobStatus, error_message: str | None = None
    ) -> CrawlJob | None:
        job = await self.get_by_id(job_id)
        if job is None:
            return None
        job.status = status
        if error_message is not None:
            job.error_message = error_message
        await self.session.flush()
        return job

    async def get_all_by_status(self, status: JobStatus) -> list[CrawlJob]:
        result = await self.session.execute(
            select(CrawlJob).where(CrawlJob.status == status)
        )
        return list(result.scalars().all())
