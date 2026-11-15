from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.agents import router as agents_router
from app.api.v1.posts import router as posts_router
from app.api.v1.comments import router as comments_router
from app.api.v1.routing import router as routing_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.dashboard import router as dashboard_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(posts_router)
api_v1_router.include_router(comments_router)
api_v1_router.include_router(routing_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(feedback_router)
api_v1_router.include_router(dashboard_router)
