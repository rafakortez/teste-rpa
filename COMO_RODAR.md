# Guia de Execução (Windows/Linux)

Este projeto foi desenvolvido e testado em ambiente Windows com Docker Desktop (WSL2 configurado).

## Pré-requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando.
- Git.

## Como Executar

1. **Clone o repositório:**
   ```powershell
   git clone <URL_DO_REPO>
   cd teste-tecnico-senior-rpa
   ```

2. **Suba os containers (Build + Run):**
   ```powershell
   docker-compose up -d --build
   ```
   *Isso iniciará a API (porta 8000), Worker, RabbitMQ e PostgreSQL. As migrações do banco rodam automaticamente.*

3. **Verifique o Status:**
   Acesse a documentação interativa da API:
   👉 [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Dispare a Coleta (Crawling):**
   Execute uma requisição POST para iniciar os jobs:
   ```powershell
   curl -X POST http://localhost:8000/crawl/all
   ```
   Ou via Swagger UI em `/crawl/all`.

5. **Acompanhe os Jobs:**
   Veja o status em tempo real:
   - **Jobs:** [http://localhost:8000/jobs](http://localhost:8000/jobs)
   - **Logs do Worker:** `docker-compose logs -f worker`

6. **Veja os Resultados:**
   Os dados coletados estarão disponíveis em JSON:
   - **Hockey:** [http://localhost:8000/results/hockey](http://localhost:8000/results/hockey)
   - **Oscar:** [http://localhost:8000/results/oscar](http://localhost:8000/results/oscar)

## Observações Técnicas

- **Persistência:** Os dados são salvos no PostgreSQL (volume docker).
- **Filas:** RabbitMQ gerencia a distribuição de jobs.
- **Resiliência:** Implementamos Logica de Retry na conexão com RabbitMQ e espera dinâmica (WebDriverWait + Sleep) no Selenium para evitar erros de renderização.

## Estrutura do Projeto
- `src/api`: Endpoints REST (FastAPI).
- `src/scrapers`: Lógica de extração (Selenium/BS4).
- `src/worker`: Consumidor de filas RabbitMQ.
- `src/models` & `src/schemas`: Definições de dados (SQLAlchemy/Pydantic).
