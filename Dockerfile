# Combined Dockerfile - All services for Data Engineering Platform
# Merged from: Dockerfile.airflow, Dockerfile.embedded, Dockerfile.fastapi, knowledge-platform/frontend/Dockerfile

# ============================================================
# Stage: airflow - Custom Airflow Image
# Source: Dockerfile.airflow
# ============================================================
FROM apache/airflow:3.3.2-python3.11 AS airflow

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://dl.min.io/client/mc/release/linux-amd64/mc \
    -o /usr/local/bin/mc && \
    chmod +x /usr/local/bin/mc

USER airflow

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres==5.9.0 \
    apache-airflow-providers-apache-spark==4.0.0 \
    apache-airflow-providers-minio==1.0.0 \
    openlineage-airflow==1.8.0 \
    dbt-postgres==1.8.0 \
    dbt-expectations==0.10.0

WORKDIR /opt/airflow

# ============================================================
# Stage: embedded - Embedded Analytics API
# Source: Dockerfile.embedded
# ============================================================
FROM python:3.13-slim AS embedded

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY embedded/ ./embedded/

EXPOSE 8080

CMD ["python", "-m", "embedded.main"]

# ============================================================
# Stage: fastapi - FastAPI Service
# Source: Dockerfile.fastapi
# ============================================================
FROM python:3.13-slim AS fastapi

WORKDIR /app

COPY requirements-fastapi.txt /app/requirements-fastapi.txt

RUN pip install --no-cache-dir --no-compile -r /app/requirements-fastapi.txt

COPY app/ /app/app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================================
# Stage: frontend - Knowledge Platform Frontend (Next.js)
# Source: knowledge-platform/frontend/Dockerfile
# ============================================================
FROM node:20-alpine AS deps-frontend
WORKDIR /app
COPY knowledge-platform/frontend/package*.json ./
RUN npm install

FROM node:20-alpine AS builder-frontend
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps-frontend /app/node_modules ./node_modules
COPY knowledge-platform/frontend/ .
RUN npm run build

FROM node:20-alpine AS frontend
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN addgroup -system -g 1001 nodejs && adduser -system -u 1001 nextjs
COPY --from=builder-frontend --chown=nextjs:nodejs /app/public ./public
COPY --from=builder-frontend --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder-frontend --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]