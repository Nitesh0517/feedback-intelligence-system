from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Overall service status")
    version: str = Field(description="API service version")
    timestamp: datetime = Field(description="Current server timestamp")
    environment: str = Field(description="Current deployment environment")


class ReadyResponse(BaseModel):
    status: str = Field(default="ready", description="Readiness status")
    database: str = Field(description="Database connectivity status: healthy or unreachable")
    redis: Optional[str] = Field(default=None, description="Redis connectivity status")
    version: str = Field(description="API service version")
    timestamp: datetime = Field(description="Current server timestamp")
