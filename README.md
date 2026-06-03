# AI SQL/Code Assistant

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![Anthropic](https://img.shields.io/badge/Anthropic-API-191919?logo=anthropic&logoColor=white) ![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=nextdotjs&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

An AI-powered assistant that turns natural language into production-ready SQL (and answers general coding questions). The reusable ai_core package is the shared **AI foundation** that the Agent Orchestrator (Project 2) builds on.

## Architecture

```
frontend (Next.js)  ──HTTP──▶  backend (FastAPI)
                               └── app/ai_core/   ◀── reused by Project 2
                                     ├── client.py   (Anthropic Messages wrapper)
                                     └── prompts.py  (versioned system prompts)
```

## Project layout

```
ai-sql-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app + CORS
│   │   ├── config.py         # typed settings from env
│   │   ├── schemas.py        # request/response models
│   │   ├── api/routes.py     # /health, /api/chat, /api/sql
│   │   └── ai_core/          # shared, framework-agnostic AI layer
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                 # Next.js client (thin)
├── docker-compose.yml
├── Makefile
└── .github/workflows/ci.yml
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- An Anthropic API key — https://console.anthropic.com
- (Optional) Docker + Docker Compose

## Setup

```bash
cp .env.example .env          # then add your ANTHROPIC_API_KEY
make install                  # backend (editable) + frontend deps
```

## Run locally

**Backend**

```bash
make dev          # http://localhost:8000  (interactive docs at /docs)
```

**Frontend** (separate terminal)

```bash
cp frontend/.env.local.example frontend/.env.local
make fe-dev       # http://localhost:3000
```

**Or with Docker** (backend + Postgres)

```bash
make up
```

## Try it

```bash
curl -s localhost:8000/api/sql \
  -H 'content-type: application/json' \
  -d '{"prompt":"top 5 customers by spend in the last 30 days","dialect":"postgres"}'
```

## Test & lint

```bash
make test
make lint
```

> The health/smoke tests run **without** a live API key, so CI stays green without secrets.

## Deploy

| Component | Suggested target | Notes |
|-----------|------------------|-------|
| Backend   | Fly.io / Render / Railway / AWS App Runner | Build from backend/Dockerfile; set ANTHROPIC_API_KEY, ALLOWED_ORIGINS. |
| Frontend  | Vercel | Set NEXT_PUBLIC_API_URL to the deployed backend URL. |

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| ANTHROPIC_API_KEY | ✅ | — | Anthropic API key |
| ANTHROPIC_MODEL | — | claude-3-5-sonnet-latest | Model ID — see https://docs.claude.com |
| MAX_TOKENS | — | 1500 | Max output tokens |
| ALLOWED_ORIGINS | — | http://localhost:3000 | Comma-separated CORS origins |
| NEXT_PUBLIC_API_URL | — | http://localhost:8000 | Backend URL used by the frontend |
