# imagem base com Python 3.13
FROM python:3.13-slim

# instala Chrome + dependencias p/ Selenium rodar headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copia dependencias primeiro (cache do Docker: so reinstala se mudar)
COPY pyproject.toml .

# instala uv e dependencias do projeto
RUN pip install uv && uv pip install --system -e ".[dev]"

# copia o codigo fonte
COPY . .

# variaveis de ambiente p/ Chrome dentro do container
ENV APP_CHROME_BINARY_PATH=/usr/bin/chromium
ENV APP_CHROMEDRIVER_PATH=/usr/bin/chromedriver

# porta padrao da API
EXPOSE 8000
