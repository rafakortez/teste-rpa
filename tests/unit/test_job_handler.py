from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.crawl_job import JobStatus, JobType
from src.worker.job_handler import handle_job


@pytest.fixture
def fake_session():
    """Sessao do banco mockada — nao conecta no banco real."""
    session = AsyncMock()
    return session


@pytest.fixture
def fake_job():
    """Job mockado com atributos minimos."""
    job = MagicMock()
    job.id = "abc-123"
    job.job_type = JobType.HOCKEY
    return job


@patch("src.worker.job_handler.HockeyTeamRepo")
@patch("src.worker.job_handler.CrawlJobRepo")
@patch("src.worker.job_handler.SCRAPER_MAP")
async def test_handle_job_hockey_completa_com_sucesso(
    mock_map, MockJobRepo, MockHockeyRepo, fake_session, fake_job
):
    # configura mock do repo de jobs
    mock_job_repo = MockJobRepo.return_value
    mock_job_repo.get_by_id = AsyncMock(return_value=fake_job)
    mock_job_repo.update_status = AsyncMock()

    # configura mock do scraper via SCRAPER_MAP
    mock_scraper = AsyncMock()
    mock_scraper.execute = AsyncMock(return_value=[
        {"team_name": "Bruins", "year": 2020, "wins": 44, "losses": 14},
        {"team_name": "Leafs", "year": 2020, "wins": 36, "losses": 25},
    ])
    mock_map.__getitem__ = MagicMock(return_value=lambda: mock_scraper)

    mock_hockey_repo = MockHockeyRepo.return_value
    mock_hockey_repo.create_many = AsyncMock()

    # executa
    await handle_job(fake_session, "abc-123", "hockey")

    # verifica que mudou status pra RUNNING e depois COMPLETED
    calls = mock_job_repo.update_status.call_args_list
    assert calls[0].args == ("abc-123", JobStatus.RUNNING)
    assert calls[1].args == ("abc-123", JobStatus.COMPLETED)

    # verifica que salvou entidades
    mock_hockey_repo.create_many.assert_called_once()


@patch("src.worker.job_handler.CrawlJobRepo")
@patch("src.worker.job_handler.SCRAPER_MAP")
async def test_handle_job_marca_failed_quando_scraper_falha(
    mock_map, MockJobRepo, fake_session, fake_job
):
    mock_job_repo = MockJobRepo.return_value
    mock_job_repo.get_by_id = AsyncMock(return_value=fake_job)
    mock_job_repo.update_status = AsyncMock()

    # scraper mockado que levanta erro
    mock_scraper = AsyncMock()
    mock_scraper.execute = AsyncMock(side_effect=Exception("Site fora do ar"))
    mock_map.__getitem__ = MagicMock(return_value=lambda: mock_scraper)

    await handle_job(fake_session, "abc-123", "hockey")

    # verifica que marcou como FAILED com a mensagem de erro
    last_call = mock_job_repo.update_status.call_args_list[-1]
    assert last_call.args == ("abc-123", JobStatus.FAILED)
    assert last_call.kwargs["error_message"] == "Site fora do ar"
