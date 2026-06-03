"""HTTP routes."""
from __future__ import annotations

from fastapi import APIRouter

from app.ai_core import CODE_SYSTEM_PROMPT, ai, build_sql_prompt
from app.config import settings
from app.schemas import (
    AssistantResponse,
    ChatRequest,
    HealthResponse,
    SQLRequest,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(model=settings.anthropic_model, env=settings.app_env)


@router.post("/api/chat", response_model=AssistantResponse)
def chat(req: ChatRequest) -> AssistantResponse:
    messages = [m.model_dump() for m in req.messages]
    content = ai.complete(messages=messages, system=CODE_SYSTEM_PROMPT)
    return AssistantResponse(content=content)


@router.post("/api/sql", response_model=AssistantResponse)
def generate_sql(req: SQLRequest) -> AssistantResponse:
    user_prompt = req.prompt
    if req.schema_ddl:
        user_prompt = f"Schema:\n{req.schema_ddl}\n\nRequest:\n{req.prompt}"

    content = ai.complete(
        messages=[{"role": "user", "content": user_prompt}],
        system=build_sql_prompt(req.dialect),
    )
    return AssistantResponse(content=content)
