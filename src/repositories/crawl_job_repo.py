from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.crawl_job import CrawlJob, JobStatus
from src.repositories.base_repository import BaseRepository


class CrawlJobRepo(BaseRepository[CrawlJob]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CrawlJob)

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        error_message: str | None = None,
        error_screenshot: bytes | None = None,
    ) -> CrawlJob | None:
        job = await self.get_by_id(job_id)
        if job is None:
            return None
        job.status = status
        if error_message is not None:
            job.error_message = error_message
        if error_screenshot is not None:
            job.error_screenshot = error_screenshot
        await self.session.flush()
        return job

    async def get_all_by_status(self, status: JobStatus) -> list[CrawlJob]:
        result = await self.session.execute(
            select(CrawlJob).where(CrawlJob.status == status)
        )
        return list(result.scalars().all())

    async def get_failed(self, limit: int = 5) -> list[CrawlJob]:
        """Retorna os ultimos N jobs com status failed, ordenados por data desc."""
        result = await self.session.execute(
            select(CrawlJob)
            .where(CrawlJob.status == JobStatus.FAILED)
            .order_by(CrawlJob.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_stats(self) -> dict[str, int]:
        """Retorna contagem de jobs agrupada por status."""
        result = await self.session.execute(
            select(CrawlJob.status, func.count(CrawlJob.id))
            .group_by(CrawlJob.status)
        )
        rows = result.all()
        # garante que todos os status aparecem, mesmo com 0
        stats = {s.value: 0 for s in JobStatus}
        for status, count in rows:
            stats[status] = count
        return stats

