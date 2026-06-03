"""Request/response models for the API."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[Message] = Field(..., min_length=1)


class SQLRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Natural-language description of the query.")
    dialect: Literal["postgres", "mysql", "sqlite", "bigquery"] = "postgres"
    schema_ddl: str | None = Field(
        default=None, description="Optional CREATE TABLE statements to ground the model."
    )


class AssistantResponse(BaseModel):
    content: str


class HealthResponse(BaseModel):
    status: str = "ok"
    model: str
    env: str
