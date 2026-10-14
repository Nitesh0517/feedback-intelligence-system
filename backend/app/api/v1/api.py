from fastapi import APIRouter
from app.api.v1 import health
from app.api.v1 import feedback
from app.api.v1 import analytics
from app.api.v1 import tasks
from app.api.v1 import auth
from app.api.v1 import users

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])


