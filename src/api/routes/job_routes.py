from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_session  # injecao da sessao
from src.models.crawl_job import JobType
from src.repositories.crawl_job_repo import CrawlJobRepo  # repo de jobs
from src.repositories.hockey_team_repo import HockeyTeamRepo
from src.repositories.oscar_film_repo import OscarFilmRepo
from src.schemas.crawl_job_response import CrawlJobResponse  # formato da resposta
from src.schemas.hockey_team_response import HockeyTeamResponse
from src.schemas.oscar_film_response import OscarFilmResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


class FailedJobSummary(BaseModel):
    """Resumo de um job falho — sem o screenshot (bytes pesados)."""
    model_config = {"from_attributes": True}
    id: str
    job_type: str
    created_at: datetime
    error_message: str | None = None
    has_screenshot: bool = False




@router.get(
    "/failed",
    response_model=list[FailedJobSummary],
    summary="Ultimos jobs com falha",
    description="Retorna os ultimos N jobs com status failed. Use o job_id para buscar o screenshot via GET /jobs/{id}/screenshot.",
)
async def get_failed_jobs(
    limit: int = 5,
    session: AsyncSession = Depends(get_session),
):
    repo = CrawlJobRepo(session)
    jobs = await repo.get_failed(limit=limit)
    return [FailedJobSummary.model_validate(j) for j in jobs]


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


@router.get(
    "/{job_id}/screenshot",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def get_job_screenshot(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Retorna screenshot de erro (PNG) se houver."""
    job_repo = CrawlJobRepo(session)
    job = await job_repo.get_by_id(job_id)
    if not job or not job.error_screenshot:
        raise HTTPException(status_code=404, detail="Screenshot not found")

    return Response(content=job.error_screenshot, media_type="image/png")
