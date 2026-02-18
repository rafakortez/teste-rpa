# Teste Técnico - Desenvolvedor Senior RPA

## Contexto

Você foi contratado para desenvolver um sistema de coleta de dados que extrai informações de múltiplas fontes web, gerencia jobs através de filas de mensagens, e disponibiliza os dados via API REST.

## Objetivo

Construir uma aplicação que:

1. Colete dados de **duas fontes distintas** com diferentes estratégias de scraping
2. Implemente um **sistema de filas com RabbitMQ** para gerenciamento de jobs
3. Persista dados em **PostgreSQL**
4. Exponha uma **API REST**
5. Tenha **testes automatizados** (unitários e integração)
6. Seja **containerizada** e executável via `docker-compose up`
7. Tenha **CI/CD** com GitHub Actions

---

## Arquitetura Esperada

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│  RabbitMQ   │────▶│   Workers   │
│    (API)    │     │   (Queue)   │     │  (Crawlers) │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                       │
       │            ┌─────────────┐            │
       └───────────▶│  PostgreSQL │◀───────────┘
                    │    (Data)   │
                    └─────────────┘
```

---

## Sites Alvo

### 1. Hockey Teams

**URL:** https://www.scrapethissite.com/pages/forms/

**Características:** Página HTML com paginação tradicional

**Dados a coletar:**
- Team Name
- Year
- Wins, Losses, OT Losses
- Win %, Goals For (GF), Goals Against (GA), Goal Difference

---

### 2. Oscar Winning Films

**URL:** https://www.scrapethissite.com/pages/ajax-javascript/

**Características:** Dados carregados via JavaScript/AJAX

**Dados a coletar:**
- Year, Title, Nominations, Awards, Best Picture

---

## Requisitos Técnicos

### Stack Obrigatória

| Tecnologia | Uso |
|------------|-----|
| **FastAPI** | Framework web |
| **Pydantic** | Validação e serialização |
| **SQLAlchemy** | ORM para persistência |
| **PostgreSQL** | Banco de dados |
| **RabbitMQ** | Sistema de filas |
| **Selenium** | Disponível para páginas dinâmicas |
| **Docker + Docker Compose** | Containerização |
| **GitHub Actions** | CI/CD |

---

## Endpoints da API (Assíncronos)

```
# Agendar coletas
POST /crawl/hockey         → Agenda coleta do Hockey (retorna job_id)
POST /crawl/oscar          → Agenda coleta do Oscar (retorna job_id)
POST /crawl/all            → Agenda ambas as coletas (retorna job_id)

# Gerenciar jobs
GET  /jobs                 → Lista todos os jobs
GET  /jobs/{job_id}        → Status e detalhes de um job

# Consultar resultados
GET  /jobs/{job_id}/results → Resultados de um job específico
GET  /results/hockey        → Todos os dados coletados de Hockey
GET  /results/oscar         → Todos os dados coletados de Oscar
```

**Fluxo assíncrono:**
1. `POST /crawl/*` publica mensagem no RabbitMQ e retorna `job_id` imediatamente
2. Worker consome a mensagem e executa o crawling
3. `GET /jobs/{job_id}` para verificar status (pending, running, completed, failed)
4. `GET /jobs/{job_id}/results` para obter os dados coletados por aquele job

---

## Testes

| Tipo | Descrição |
|------|-----------|
| **Unitários** | Testar lógica de negócio, parsers, validações |
| **Integração** | Testar API, filas e banco usando Testcontainers |

**Não é necessário** testar crawling real contra os sites.

---

## CI/CD com GitHub Actions

O pipeline deve executar:

1. **Lint** - Verificar código (ruff, black, etc.)
2. **Testes unitários** - pytest
3. **Testes de integração** - pytest com Testcontainers
4. **Build** - Construir imagem Docker
5. **Push** - Enviar imagem para Google Container Registry (GCR)

---

## Critérios de Avaliação

| Critério | Peso |
|----------|------|
| **Arquitetura** | Alto - Design, separação de responsabilidades, uso do RabbitMQ |
| **Qualidade de código** | Alto - SOLID, tipagem, boas práticas |
| **Funcionamento** | Alto - A solução deve funcionar corretamente |
| **Testes** | Alto - Unitários e integração com Testcontainers |
| **CI/CD** | Alto - Pipeline funcional com push para GCR |
| **Tratamento de erros** | Médio - Robustez e resiliência |
| **Documentação** | Baixo |

---

## Ambiente de Desenvolvimento

### Nix + direnv (Recomendado - Linux)

#### 1. Instalar Nix

```bash
sh <(curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install) --daemon
```

#### 2. Habilitar Flakes

Adicione ao `~/.config/nix/nix.conf`:

```
experimental-features = nix-command flakes
```

#### 3. Instalar direnv

```bash
# Debian/Ubuntu
sudo apt install direnv

# Fedora
sudo dnf install direnv

# Arch
sudo pacman -S direnv
```

Adicione ao seu shell (`~/.bashrc` ou `~/.zshrc`):

```bash
eval "$(direnv hook bash)"  # ou zsh
```

#### 4. Rodar

O `.envrc` e `flake.nix` já vêm prontos no repositório. Basta permitir o direnv e o ambiente será carregado automaticamente:

```bash
direnv allow
```

Commite o `flake.lock` no seu repositório.

---

## Regras

1. **Entrega:** Fork deste repositório
2. **Dúvidas:** ti@bpcreditos.com.br | gabrielpelizzaro@gmail.com

---

**Queremos ver como você arquiteta soluções, não apenas como escreve código.**
