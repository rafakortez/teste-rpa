from fastapi import APIRouter, Depends, HTTPException  # HTTPException p/ erros HTTP
from sqlalchemy.ext.asyncio import AsyncSession  # tipo da sessao do banco

from src.api.dependencies import get_session  # injecao da sessao
from src.repositories.crawl_job_repo import CrawlJobRepo  # repo de jobs
from src.repositories.hockey_team_repo import HockeyTeamRepo  # repo de hockey
from src.repositories.oscar_film_repo import OscarFilmRepo  # repo de oscar
from src.schemas.hockey_team_response import HockeyTeamResponse  # formato hockey
from src.schemas.oscar_film_response import OscarFilmResponse  # formato oscar

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/hockey", response_model=list[HockeyTeamResponse])
async def get_all_hockey(session: AsyncSession = Depends(get_session)):
    """Retorna todos os dados coletados de hockey (todos os jobs)."""
    repo = HockeyTeamRepo(session)
    teams = await repo.get_all()
    return [HockeyTeamResponse.model_validate(t) for t in teams]


@router.get("/oscar", response_model=list[OscarFilmResponse])
async def get_all_oscar(session: AsyncSession = Depends(get_session)):
    """Retorna todos os dados coletados de oscar (todos os jobs)."""
    repo = OscarFilmRepo(session)
    films = await repo.get_all()
    return [OscarFilmResponse.model_validate(f) for f in films]


@router.get("/hockey/{job_id}", response_model=list[HockeyTeamResponse])
async def get_hockey_results(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    # verifica se job existe antes de buscar result
    job_repo = CrawlJobRepo(session)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    repo = HockeyTeamRepo(session)
    teams = await repo.get_by_job_id(job_id)
    return [HockeyTeamResponse.model_validate(t) for t in teams]


@router.get("/oscar/{job_id}", response_model=list[OscarFilmResponse])
async def get_oscar_results(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    # verifica se o job existe antes de buscar resultados
    job_repo = CrawlJobRepo(session)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    repo = OscarFilmRepo(session)
    films = await repo.get_by_job_id(job_id)
    return [OscarFilmResponse.model_validate(f) for f in films]
