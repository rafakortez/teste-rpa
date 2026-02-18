
from src.models.crawl_job import CrawlJob, JobStatus, JobType
from src.repositories.crawl_job_repo import CrawlJobRepo


async def test_cria_e_busca_job(session):
    """Testa CRUD completo num Postgres real."""
    repo = CrawlJobRepo(session)

    # cria
    job = CrawlJob(job_type=JobType.HOCKEY)
    created = await repo.create(job)
    await session.commit()

    assert created.id is not None
    assert created.status == JobStatus.PENDING

    # busca por id
    found = await repo.get_by_id(created.id)
    assert found is not None
    assert found.job_type == JobType.HOCKEY


async def test_update_status_muda_pra_completed(session):
    repo = CrawlJobRepo(session)

    job = CrawlJob(job_type=JobType.OSCAR)
    await repo.create(job)
    await session.commit()

    # muda status
    updated = await repo.update_status(job.id, JobStatus.COMPLETED)
    await session.commit()

    assert updated.status == JobStatus.COMPLETED


async def test_update_status_com_erro_salva_mensagem(session):
    repo = CrawlJobRepo(session)

    job = CrawlJob(job_type=JobType.HOCKEY)
    await repo.create(job)
    await session.commit()

    # simula falha
    await repo.update_status(job.id, JobStatus.FAILED, error_message="Timeout")
    await session.commit()

    found = await repo.get_by_id(job.id)
    assert found.status == JobStatus.FAILED
    assert found.error_message == "Timeout"


async def test_get_all_retorna_lista(session):
    repo = CrawlJobRepo(session)

    await repo.create(CrawlJob(job_type=JobType.HOCKEY))
    await repo.create(CrawlJob(job_type=JobType.OSCAR))
    await session.commit()

    jobs = await repo.get_all()
    assert len(jobs) >= 2
