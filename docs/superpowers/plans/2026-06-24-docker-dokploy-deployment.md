# Configuração de Docker e Dokploy para Produção Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preparar e configurar a arquitetura Docker/Docker Compose para deploy seguro no Dokploy com PostgreSQL e suporte a origens CSRF dinâmicas.

**Architecture:**
- Atualizar a configuração `CSRF_TRUSTED_ORIGINS` em `core/settings.py`.
- Ajustar `entrypoint.prod.sh` para expor a aplicação externamente no container (`--bind 0.0.0.0:8000`).
- Criar o arquivo `docker-compose.yml` no diretório raiz do projeto.

**Tech Stack:** Docker, Docker Compose, PostgreSQL 16, Django 6, Gunicorn.

## Global Constraints

- Garantir que as configurações sejam 100% retrocompatíveis com o ambiente de testes local.
- Não incluir credenciais expostas nos arquivos de configuração do Docker.

---

### Task 1: Configurar Origens CSRF Dinâmicas no Django

**Files:**
- Modify: `core/settings.py:19-20`
- Test: `./.venv/bin/python manage.py test`

**Interfaces:**
- Consumes: Nenhuma
- Produces: `CSRF_TRUSTED_ORIGINS` dinâmico via decouple `config`.

- [ ] **Step 1: Modificar o carregamento da lista de origens confiáveis**
Substituir a declaração estática na linha 19 de `core/settings.py` para carregar do ambiente via decouple `config`.

Código anterior:
```python
CSRF_TRUSTED_ORIGINS = ['https://*.railway.app']
```

Novo código:
```python
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://*.railway.app').split(',')
```

- [ ] **Step 2: Rodar os testes automatizados para verificar integridade**
Run: `./.venv/bin/python manage.py test`
Expected: `Ran 45 tests in ... OK`

- [ ] **Step 3: Commit**
```bash
git add core/settings.py
git commit -m "chore(settings): load CSRF_TRUSTED_ORIGINS dynamically from environment"
```

---

### Task 2: Ajustar Script de Inicialização da Produção

**Files:**
- Modify: `entrypoint.prod.sh`

**Interfaces:**
- Consumes: Nenhuma
- Produces: Script de entrypoint ajustado para expor a porta e sincronizar arquivos.

- [ ] **Step 1: Atualizar o arquivo `entrypoint.prod.sh`**
Substituir o conteúdo do arquivo `entrypoint.prod.sh` para rodar migrações, coletar arquivos estáticos e ligar o Gunicorn escutando em `0.0.0.0:8000`.

Código anterior:
```bash
#!/usr/bin/env bash

python manage.py migrate --noinput &&
python manage.py collectstatic --noinput &

gunicorn core.wsgi
```

Novo código:
```bash
#!/usr/bin/env bash

echo "Rodando migrações do banco..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor Gunicorn..."
gunicorn core.wsgi --bind 0.0.0.0:8000
```

- [ ] **Step 2: Commit**
```bash
git add entrypoint.prod.sh
git commit -m "deploy(docker): update production entrypoint to bind gunicorn to 0.0.0.0:8000"
```

---

### Task 3: Criar o Docker Compose

**Files:**
- Create: `docker-compose.yml`

**Interfaces:**
- Consumes: `Dockerfile`, `entrypoint.prod.sh`
- Produces: Configuração do compose para o Dokploy.

- [ ] **Step 1: Criar o arquivo `docker-compose.yml` na raiz do projeto**
Adicionar a definição de serviços `web` e `db` com suas respectivas dependências e volumes.

Conteúdo do arquivo:
```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    image: lead-scout-ai:latest
    restart: always
    expose:
      - "8000"
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-*}
      - CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}
      - PGDATABASE=${PGDATABASE}
      - PGUSER=${PGUSER}
      - PGPASSWORD=${PGPASSWORD}
      - PGHOST=db
      - PGPORT=5432
      - SERPER_API_KEY=${SERPER_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    restart: always
    environment:
      - POSTGRES_DB=${PGDATABASE}
      - POSTGRES_USER=${PGUSER}
      - POSTGRES_PASSWORD=${PGPASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${PGUSER} -d $${PGDATABASE}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

- [ ] **Step 2: Verificar a sintaxe do Docker Compose localmente**
Run: `docker compose config`
Expected: Exibe a configuração parseada com sucesso (ou avisa sobre variáveis ausentes no shell, o que é esperado pois usaremos o env em produção).

- [ ] **Step 3: Commit**
```bash
git add docker-compose.yml docs/superpowers/plans/2026-06-24-docker-dokploy-deployment.md docs/superpowers/specs/2026-06-24-docker-dokploy-deployment-design.md
git commit -m "deploy(docker): create production docker-compose.yml configuration"
```
