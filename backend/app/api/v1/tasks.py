from fastapi import APIRouter, Depends, status
from celery.result import AsyncResult
from app.tasks.celery_app import celery_app
from app.schemas.tasks import TaskStatusResponse
from app.api.deps import require_authenticated
from app.core.logging import logger

router = APIRouter(dependencies=[Depends(require_authenticated)])



@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get background task status",
)
def get_task_status(task_id: str):
    """
    Retrieves execution state, completion status, and results for a background Celery task.
    """
    async_result = AsyncResult(task_id, app=celery_app)
    
    state = async_result.state
    is_ready = async_result.ready()
    is_successful = async_result.successful() if is_ready else None
    
    result_data = None
    error_msg = None
    
    if is_ready:
        if async_result.failed():
            error_msg = str(async_result.result)
        else:
            result_data = async_result.result
            if isinstance(result_data, dict) and result_data.get("status") == "failed":
                error_msg = result_data.get("error")
                
    return TaskStatusResponse(
        task_id=task_id,
        status=state,
        ready=is_ready,
        successful=is_successful if error_msg is None else False,
        result=result_data,
        error=error_msg,
    )
