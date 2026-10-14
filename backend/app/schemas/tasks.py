from typing import Any, Optional
from pydantic import BaseModel, Field


class TaskEnqueueResponse(BaseModel):
    task_id: str = Field(..., description="Unique Celery task identifier")
    status: str = Field(default="PENDING", description="Initial task status")
    message: str = Field(default="Task submitted successfully", description="Status message")


class TaskStatusResponse(BaseModel):
    task_id: str = Field(..., description="Unique Celery task identifier")
    status: str = Field(..., description="Current Celery status: PENDING, STARTED, SUCCESS, FAILURE, etc.")
    ready: bool = Field(..., description="True if task has completed execution (success or failure)")
    successful: Optional[bool] = Field(default=None, description="True if task finished successfully without unhandled exception")
    result: Optional[Any] = Field(default=None, description="Task execution output or details")
    error: Optional[str] = Field(default=None, description="Error message if task failed")
