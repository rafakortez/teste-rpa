import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.crawl_job import JobStatus, JobType
from src.models.hockey_team import HockeyTeam
from src.models.oscar_film import OscarFilm
from src.repositories.crawl_job_repo import CrawlJobRepo
from src.repositories.hockey_team_repo import HockeyTeamRepo
from src.repositories.oscar_film_repo import OscarFilmRepo
from src.scrapers.hockey_scraper import HockeyScraper
from src.scrapers.oscar_scraper import OscarScraper
from src.scrapers.oscar_fail_scraper import OscarFailScraper

logger = logging.getLogger(__name__)

# mapeia tipo do job pro scraper correto (Open/Closed: adicionar scraper = add entrada aqui)
SCRAPER_MAP = {
    JobType.HOCKEY: HockeyScraper,
    JobType.OSCAR: OscarScraper,
    JobType.OSCAR_FAIL: OscarFailScraper,  # simula falha de CSS em producao
}


async def handle_job(session: AsyncSession, job_id: str, job_type: str) -> None:
    job_repo = CrawlJobRepo(session)
    job = await job_repo.get_by_id(job_id)
    if not job:
        logger.error("Job %s nao encontrado no banco", job_id)
        return

    try:
        await job_repo.update_status(job_id, JobStatus.RUNNING)
        await session.commit()

        # escolhe o scraper pelo tipo do job
        scraper_class = SCRAPER_MAP[JobType(job_type)]
        scraper = scraper_class()
        raw_data = await scraper.execute()

        # salva os dados scrapeados no banco
        if job_type == JobType.HOCKEY.value:
            repo = HockeyTeamRepo(session)
            entities = [HockeyTeam(job_id=job_id, **row) for row in raw_data]
            await repo.create_many(entities)
        else:
            repo = OscarFilmRepo(session)
            entities = [OscarFilm(job_id=job_id, **row) for row in raw_data]
            await repo.create_many(entities)

        await job_repo.update_status(job_id, JobStatus.COMPLETED)
        await session.commit()
        logger.info("Job %s completado com %d registros", job_id, len(raw_data))

    except Exception as e:
        await session.rollback()
        # salva a mensagem de erro no job
        screenshot = getattr(e, "screenshot_bytes", None)
        await job_repo.update_status(
            job_id, 
            JobStatus.FAILED, 
            error_message=str(e),
            error_screenshot=screenshot
        )
        await session.commit()
        logger.exception("Job %s falhou: %s", job_id, e)
