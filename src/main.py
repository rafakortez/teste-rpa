from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.dependencies import shutdown_rabbit, startup_rabbit
from src.api.routes.crawl_routes import router as crawl_router
from src.api.routes.job_routes import router as job_router
from src.api.routes.result_routes import router as result_router


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


@app.get("/health")
async def health():
    """Endpoint simples p/ Docker/k8s verificar se a API ta viva."""
    return {"status": "ok"}
