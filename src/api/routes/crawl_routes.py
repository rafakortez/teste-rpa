import aio_pika  # cliente RabbitMQ
from fastapi import APIRouter, Depends  # roteador + injecao de dependencias
from sqlalchemy.ext.asyncio import AsyncSession  # tipo da sessao do banco

from src.api.dependencies import get_channel, get_session  # funcoes que criam sessao/canal
from src.models.crawl_job import CrawlJob, JobType  # model + enum do banco
from src.queue.rabbit_publisher import publish_crawl_job  # funcao que publica na fila
from src.repositories.crawl_job_repo import CrawlJobRepo  # repo pra salvar job
from src.schemas.crawl_job_response import CrawlJobResponse  # formato da resposta JSON

router = APIRouter(prefix="/crawl", tags=["crawl"])

@router.post("/hockey", response_model=CrawlJobResponse)
async def crawl_hockey(
    session: AsyncSession = Depends(get_session),
    channel: aio_pika.abc.AbstractChannel = Depends(get_channel),
):
    repo = CrawlJobRepo(session)
    job = CrawlJob(job_type=JobType.HOCKEY)
    await repo.create(job)

    # publica na fila p/ worker processar em background
    await publish_crawl_job(channel, job.id, job.job_type.value)

    await session.commit()
    return CrawlJobResponse.model_validate(job)


@router.post("/oscar", response_model=CrawlJobResponse)
async def crawl_oscar(
    session: AsyncSession = Depends(get_session),
    channel: aio_pika.abc.AbstractChannel = Depends(get_channel),
):
    repo = CrawlJobRepo(session)
    job = CrawlJob(job_type=JobType.OSCAR)
    await repo.create(job)

    # publica na fila p/ worker processar em background
    await publish_crawl_job(channel, job.id, job.job_type.value)

    await session.commit()
    return CrawlJobResponse.model_validate(job)


@router.post("/all", response_model=list[CrawlJobResponse])
async def crawl_all(
    session: AsyncSession = Depends(get_session),
    channel: aio_pika.abc.AbstractChannel = Depends(get_channel),
):
    repo = CrawlJobRepo(session)
    jobs = []

    for job_type in [JobType.HOCKEY, JobType.OSCAR]:
        job = CrawlJob(job_type=job_type)
        await repo.create(job)
        await publish_crawl_job(channel, job.id, job.job_type.value)
        jobs.append(job)

    await session.commit()
    return [CrawlJobResponse.model_validate(j) for j in jobs]


@router.post(
    "/oscar_fail",
    response_model=CrawlJobResponse,
    summary="Simula falha de scraper (demo de observabilidade)",
    description=(
        "Cria um job oscar que vai falhar intencionalmente, simulando uma mudança "
        "de estrutura CSS no site alvo. Útil para demonstrar o endpoint de screenshot "
        "de erro: GET /jobs/{id}/screenshot."
    ),
)
async def crawl_oscar_fail(
    session: AsyncSession = Depends(get_session),
    channel: aio_pika.abc.AbstractChannel = Depends(get_channel),
):
    repo = CrawlJobRepo(session)
    job = CrawlJob(job_type=JobType.OSCAR_FAIL)
    await repo.create(job)
    await publish_crawl_job(channel, job.id, job.job_type.value)
    await session.commit()
    return CrawlJobResponse.model_validate(job)
