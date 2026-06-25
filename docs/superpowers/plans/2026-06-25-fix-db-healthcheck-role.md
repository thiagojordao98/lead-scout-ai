# Fix Database Healthcheck Role Error Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the `FATAL: role "-d" does not exist` database log messages by fixing the pg_isready healthcheck command and adding fallback default values for database variables.

**Architecture:** Use docker-compose variable fallbacks (`${VAR:-default}`) to ensure default username/database credentials are used when host variables are not set, and update the healthcheck command to reference the resolved container environment variables (`POSTGRES_USER` and `POSTGRES_DB`).

**Tech Stack:** Docker, Docker Compose, PostgreSQL

## Global Constraints

- Keep variables flexible to support both local development (where PG variables are unset) and production (where PG variables are injected).
- Verify container execution and check logs to confirm the error is gone.

---

### Task 1: Update docker-compose.yml, Design Spec, and Verify Fix

**Files:**
- Modify: [docker-compose.yml](file:///home/thiago/www/micro-saas/lead-scout-ai/docker-compose.yml)
- Modify: [docs/superpowers/specs/2026-06-24-docker-dokploy-deployment-design.md](file:///home/thiago/www/micro-saas/lead-scout-ai/docs/superpowers/specs/2026-06-24-docker-dokploy-deployment-design.md)

**Interfaces:**
- Consumes: Existing docker-compose and design spec configuration
- Produces: Corrected docker-compose setup and design spec with fallback db variables and working healthcheck

- [ ] **Step 1: Edit docker-compose.yml**
  Modify [docker-compose.yml](file:///home/thiago/www/micro-saas/lead-scout-ai/docker-compose.yml) to add fallback defaults for database variables and update the healthcheck command.
  Replace the environment and healthcheck sections of both services with fallbacks and correct container environment variable references.

- [ ] **Step 2: Edit docs/superpowers/specs/2026-06-24-docker-dokploy-deployment-design.md**
  Modify [docs/superpowers/specs/2026-06-24-docker-dokploy-deployment-design.md](file:///home/thiago/www/micro-saas/lead-scout-ai/docs/superpowers/specs/2026-06-24-docker-dokploy-deployment-design.md) to reflect the corrected environment variables and healthcheck command.

- [ ] **Step 3: Stop existing containers and clean volumes**
  Run: `docker compose down -v`
  Expected: Containers stopped and volumes removed.

- [ ] **Step 4: Run the database service**
  Run: `docker compose up -d db`
  Expected: Database container starts up successfully.

- [ ] **Step 5: Inspect logs for errors**
  Wait 15 seconds, then run: `docker compose logs db`
  Expected: Database initialized successfully without `FATAL: role "-d" does not exist` error.

- [ ] **Step 6: Verify healthcheck status**
  Run: `docker compose ps`
  Expected: Status for the `db` container shows `(healthy)`.

- [ ] **Step 7: Commit changes**
  Run:
  ```bash
  git add docker-compose.yml docs/superpowers/specs/2026-06-24-docker-dokploy-deployment-design.md
  git commit -m "fix(docker): resolve pg_isready role error in healthcheck and add pg fallbacks"
  ```
