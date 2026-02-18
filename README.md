# Crawler Distribuído — Teste Técnico Senior RPA

FastAPI + RabbitMQ + PostgreSQL + Selenium, containerizado com Docker Compose.

## Execução

```bash
git clone <URL_DO_REPO> && cd teste-tecnico-senior-rpa
docker-compose up -d --build
```

API em `http://localhost:8000/docs`.

## Estrutura

```
src/
├── api/          # FastAPI — rotas e dependências
├── scrapers/     # Selenium + BS4 — um scraper por fonte
├── worker/       # Consumidor RabbitMQ — processa jobs em background
├── models/       # SQLAlchemy
├── schemas/      # Pydantic
└── repositories/ # Padrão Repository — isola acesso ao banco
```

## Design

- **Single Responsibility** — cada scraper cuida de uma fonte (`HockeyScraper`, `OscarScraper`)
- **Open/Closed** — novo scraper = nova entrada no `SCRAPER_MAP`, sem alterar o Worker
- **Dependency Inversion** — API e Worker dependem de `CrawlJobRepo`, não do banco diretamente

## Endpoints

```
POST /crawl/all          inicia Hockey + Oscar
POST /crawl/oscar_fail   simula falha de CSS (demo de observabilidade)

GET  /stats              contagem de jobs por status
GET  /jobs               lista todos os jobs
GET  /jobs/failed        últimos N falhos com job_id e timestamp
GET  /jobs/{id}/screenshot  screenshot do browser no momento do erro (PNG)

GET  /results/hockey
GET  /results/oscar

GET  /health
```

## Observabilidade

Quando o Selenium falha, o Worker captura o screenshot do browser no momento exato do erro e salva no banco. Para testar:

```bash
curl -X POST http://localhost:8000/crawl/oscar_fail
curl http://localhost:8000/jobs/failed
curl http://localhost:8000/jobs/{id}/screenshot --output erro.png
```
