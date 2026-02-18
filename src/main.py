import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_session, shutdown_rabbit, startup_rabbit
from src.api.routes.crawl_routes import router as crawl_router
from src.api.routes.job_routes import router as job_router
from src.api.routes.result_routes import router as result_router

# Garante diretorio de logs
os.makedirs("logs", exist_ok=True)

# Configura logging raiz
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/api-{datetime.now().date()}.log"),
    ],
)


# lifespan controla o que roda ao iniciar e ao parar a API
@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_rabbit()   # abre conexao RabbitMQ uma vez
    yield                    # API rodando, aceita requests
    await shutdown_rabbit()  # fecha conexao ao parar


app = FastAPI(
    title="Scraper API",
    version="1.0",
    lifespan=lifespan,
)

# registra os 3 grupos de rotas
app.include_router(crawl_router)    # POST /crawl/hockey, POST /crawl/oscar
app.include_router(job_router)      # GET /jobs/, GET /jobs/{id}
app.include_router(result_router)   # GET /results/hockey/{id}, GET /results/oscar/{id}


@app.get("/health", tags=["system"])
async def health():
    """Verifica se a API esta respondendo."""
    return {"status": "ok"}


@app.get("/stats", tags=["system"], summary="Resumo de saude do sistema")
async def stats(session: AsyncSession = Depends(get_session)):
    """Retorna contagem de jobs agrupada por status (pending, running, completed, failed)."""
    from src.repositories.crawl_job_repo import CrawlJobRepo
    repo = CrawlJobRepo(session)
    return await repo.get_stats()

