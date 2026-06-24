# Design Spec: Configuração de Docker e Dokploy para Produção

**Data:** 2026-06-24  
**Status:** Aprovado pelo Usuário  
**Autor:** Antigravity

## 1. Objetivo
Preparar a aplicação para ser executada em um ambiente de produção autocontido em uma VM gerenciada via painel Dokploy, utilizando Docker Compose (App Django + PostgreSQL) e ajustando configurações de rede e segurança do Django.

## 2. Componentes e Arquitetura

### 2.1. Docker Compose (`docker-compose.yml`)
Fará a orquestração de dois serviços principais:
1. **`db`**: Serviço PostgreSQL na versão `16-alpine`. Contém volume persistente (`postgres_data`) e healthcheck para garantir integridade.
2. **`web`**: A aplicação Django empacotada. Depende de o `db` estar saudável para iniciar. Mapeia a porta `8000`.

### 2.2. Script de Inicialização (`entrypoint.prod.sh`)
* Executa migrações (`migrate`).
* Coleta arquivos estáticos (`collectstatic`) de forma síncrona.
* Inicializa o Gunicorn escutando em `0.0.0.0:8000` (porta interna mapeada pelo Docker).

### 2.3. Segurança Django (`core/settings.py`)
Permite a passagem dinâmica da variável de ambiente `CSRF_TRUSTED_ORIGINS`, separando origens autorizadas por vírgula. Isso evita bloqueios de requisições POST em produção.

## 3. Alterações Propostas

### 3.1. Arquivo `docker-compose.yml` (Criar)
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

### 3.2. Arquivo `entrypoint.prod.sh` (Modificar)
```bash
#!/usr/bin/env bash

echo "Rodando migrações do banco..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor Gunicorn..."
gunicorn core.wsgi --bind 0.0.0.0:8000
```

### 3.3. Arquivo `core/settings.py` (Modificar)
```python
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://*.railway.app').split(',')
```
