from fastapi import APIRouter, Depends, HTTPException  # HTTPException p/ erros HTTP
from sqlalchemy.ext.asyncio import AsyncSession  # tipo da sessao do banco

from src.api.dependencies import get_session  # injecao da sessao
from src.models.crawl_job import JobType
from src.repositories.crawl_job_repo import CrawlJobRepo  # repo de jobs
from src.repositories.hockey_team_repo import HockeyTeamRepo
from src.repositories.oscar_film_repo import OscarFilmRepo
from src.schemas.crawl_job_response import CrawlJobResponse  # formato da resposta
from src.schemas.hockey_team_response import HockeyTeamResponse
from src.schemas.oscar_film_response import OscarFilmResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[CrawlJobResponse])
async def list_jobs(
    session: AsyncSession = Depends(get_session),
):
    repo = CrawlJobRepo(session)
    jobs = await repo.get_all()
    return [CrawlJobResponse.model_validate(j) for j in jobs]


@router.get("/{job_id}", response_model=CrawlJobResponse)
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    repo = CrawlJobRepo(session)
    job = await repo.get_by_id(job_id)
    if not job:
        # retorna 404 se job n existe
        raise HTTPException(status_code=404, detail="Job not found")
    return CrawlJobResponse.model_validate(job)


@router.get("/{job_id}/results")
async def get_job_results(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Retorna resultados de um job especifico, detectando o tipo automaticamente."""
    job_repo = CrawlJobRepo(session)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.job_type == JobType.HOCKEY:
        repo = HockeyTeamRepo(session)
        data = await repo.get_by_job_id(job_id)
        return [HockeyTeamResponse.model_validate(d) for d in data]

    repo = OscarFilmRepo(session)
    data = await repo.get_by_job_id(job_id)
    return [OscarFilmResponse.model_validate(d) for d in data]
