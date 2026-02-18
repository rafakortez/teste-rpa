from fastapi import APIRouter, Depends, HTTPException  # HTTPException p/ erros HTTP
from sqlalchemy.ext.asyncio import AsyncSession         # tipo da sessao do banco

from src.api.dependencies import get_session             # injecao da sessao
from src.repositories.crawl_job_repo import CrawlJobRepo # repo de jobs
from src.schemas.crawl_job_response import CrawlJobResponse  # formato da resposta

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
